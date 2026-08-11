from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import chain
from typing import Iterable

from video_editing_agent.application.ports.artifact_store import (
    ArtifactPayload,
    ArtifactStore,
    StoredArtifactRef,
)
from video_editing_agent.domain.asset.model import Asset
from video_editing_agent.domain.asset.policy import AssetUsageRole, is_visual_resolver_eligible
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shot.analysis import ShotAnalysis, ShotAnalysisRef
from video_editing_agent.domain.shot.model import Shot

REFERENCE_STYLE_EVIDENCE_SCHEMA_VERSION = "r0.7b-v1"
REFERENCE_STYLE_EVIDENCE_MEDIA_TYPE = (
    "application/vnd.video-editing-agent.reference-style-evidence+json"
)
_UNAVAILABLE_DIMENSIONS = (
    "caption_density",
    "music_cut_relationship",
    "speech_structure",
    "transition_effects",
)


@dataclass(frozen=True, slots=True)
class ReferencePatternCount:
    value: str
    count: int

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("reference pattern value must not be empty")
        if isinstance(self.count, bool) or not isinstance(self.count, int):
            raise TypeError("reference pattern count must be an int")
        if self.count < 1:
            raise ValueError("reference pattern count must be >= 1")


@dataclass(frozen=True, slots=True)
class ReferenceStyleEvidence:
    """Abstract reference technique derived from exact Shot/ShotAnalysis revisions."""

    reference_asset_ref: EntityRevisionRef
    shot_refs: tuple[EntityRevisionRef, ...]
    analysis_refs: tuple[ShotAnalysisRef, ...]
    total_duration: MediaTime
    minimum_shot_duration: MediaTime
    median_shot_duration: MediaTime
    maximum_shot_duration: MediaTime
    opening_framing: str | None
    opening_camera_motion: str | None
    framing_sequence: tuple[str, ...]
    camera_motion_sequence: tuple[str, ...]
    framing_patterns: tuple[ReferencePatternCount, ...]
    camera_motion_patterns: tuple[ReferencePatternCount, ...]
    action_patterns: tuple[ReferencePatternCount, ...]
    subject_patterns: tuple[ReferencePatternCount, ...]
    environment_patterns: tuple[ReferencePatternCount, ...]
    unavailable_dimensions: tuple[str, ...] = _UNAVAILABLE_DIMENSIONS
    schema_version: str = REFERENCE_STYLE_EVIDENCE_SCHEMA_VERSION

    @property
    def shot_count(self) -> int:
        return len(self.shot_refs)


@dataclass(frozen=True, slots=True)
class ReferenceStyleEvidenceResult:
    evidence: ReferenceStyleEvidence
    artifact_ref: StoredArtifactRef
    planning_guidance: tuple[str, ...]


class ReferenceStyleEvidenceService:
    """Create cacheable reference-only evidence without granting source eligibility."""

    def __init__(self, artifact_store: ArtifactStore) -> None:
        self._artifact_store = artifact_store

    def analyze(
        self,
        reference_asset: Asset,
        shots: tuple[Shot, ...],
        analyses: tuple[ShotAnalysis, ...],
    ) -> ReferenceStyleEvidenceResult:
        asset_ref = _asset_ref(reference_asset)
        _validate_reference_asset(reference_asset)
        ordered_shots = _validate_and_order_shots(asset_ref, shots)
        ordered_analyses = _validate_and_order_analyses(ordered_shots, analyses)

        durations = tuple(shot.source_range.duration for shot in ordered_shots)
        visuals = tuple(analysis.visual for analysis in ordered_analyses)
        if not any(visual is not None for visual in visuals):
            raise ValueError("reference style evidence requires at least one visual ShotAnalysis")

        framing_sequence = tuple(
            _sequence_value(None if visual is None else visual.framing) for visual in visuals
        )
        motion_sequence = tuple(
            _sequence_value(None if visual is None else visual.camera_motion)
            for visual in visuals
        )
        opening_visual = visuals[0]

        evidence = ReferenceStyleEvidence(
            reference_asset_ref=asset_ref,
            shot_refs=tuple(_shot_ref(shot) for shot in ordered_shots),
            analysis_refs=tuple(analysis.ref for analysis in ordered_analyses),
            total_duration=_sum_times(durations),
            minimum_shot_duration=min(durations, key=lambda item: item.as_fraction()),
            median_shot_duration=_median_time(durations),
            maximum_shot_duration=max(durations, key=lambda item: item.as_fraction()),
            opening_framing=_clean_optional(
                None if opening_visual is None else opening_visual.framing
            ),
            opening_camera_motion=_clean_optional(
                None if opening_visual is None else opening_visual.camera_motion
            ),
            framing_sequence=framing_sequence,
            camera_motion_sequence=motion_sequence,
            framing_patterns=_pattern_counts(
                None if visual is None else visual.framing for visual in visuals
            ),
            camera_motion_patterns=_pattern_counts(
                None if visual is None else visual.camera_motion for visual in visuals
            ),
            action_patterns=_pattern_counts(
                chain.from_iterable(
                    () if visual is None else visual.actions for visual in visuals
                )
            ),
            subject_patterns=_pattern_counts(
                chain.from_iterable(
                    () if visual is None else visual.subjects for visual in visuals
                )
            ),
            environment_patterns=_pattern_counts(
                None if visual is None else visual.environment for visual in visuals
            ),
        )
        payload = _encode_evidence(evidence)
        artifact_ref = self._artifact_store.put(
            ArtifactPayload(
                media_type=REFERENCE_STYLE_EVIDENCE_MEDIA_TYPE,
                content=payload,
            )
        )
        return ReferenceStyleEvidenceResult(
            evidence=evidence,
            artifact_ref=artifact_ref,
            planning_guidance=_planning_guidance(evidence, artifact_ref),
        )


def _asset_ref(asset: Asset) -> EntityRevisionRef:
    return EntityRevisionRef(asset.envelope.id, asset.envelope.revision)


def _shot_ref(shot: Shot) -> EntityRevisionRef:
    return EntityRevisionRef(shot.envelope.id, shot.envelope.revision)


def _validate_reference_asset(asset: Asset) -> None:
    if asset.media_kind.strip().casefold() != "video":
        raise ValueError("reference style evidence currently requires a video Asset")
    if asset.usage_role is not AssetUsageRole.REFERENCE_ANALYSIS_ONLY:
        raise ValueError("reference Asset must use reference_analysis_only")
    if is_visual_resolver_eligible(
        media_kind=asset.media_kind,
        origin=asset.origin,
        usage_role=asset.usage_role,
    ):
        raise AssertionError("reference-analysis-only Asset must never be Resolver eligible")


def _validate_and_order_shots(
    asset_ref: EntityRevisionRef,
    shots: tuple[Shot, ...],
) -> tuple[Shot, ...]:
    if not shots:
        raise ValueError("reference style evidence requires at least one Shot")
    refs = tuple(_shot_ref(shot) for shot in shots)
    if len(set(refs)) != len(refs):
        raise ValueError("reference Shots must not contain duplicate exact revisions")
    if any(shot.asset_ref != asset_ref for shot in shots):
        raise ValueError("every reference Shot must belong to the exact reference Asset revision")
    return tuple(sorted(shots, key=lambda shot: shot.source_range.start.as_fraction()))


def _validate_and_order_analyses(
    ordered_shots: tuple[Shot, ...],
    analyses: tuple[ShotAnalysis, ...],
) -> tuple[ShotAnalysis, ...]:
    by_shot: dict[EntityRevisionRef, ShotAnalysis] = {}
    for analysis in analyses:
        if analysis.shot_ref in by_shot:
            raise ValueError("reference analyses must contain one revision per exact Shot")
        by_shot[analysis.shot_ref] = analysis

    shot_refs = tuple(_shot_ref(shot) for shot in ordered_shots)
    if set(by_shot) != set(shot_refs):
        raise ValueError("reference analysis set must exactly cover the supplied Shots")
    return tuple(by_shot[shot_ref] for shot_ref in shot_refs)


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _sequence_value(value: str | None) -> str:
    return _clean_optional(value) or "unknown"


def _pattern_counts(values: Iterable[str | None]) -> tuple[ReferencePatternCount, ...]:
    normalized = (_clean_optional(value) for value in values)
    counter = Counter(value for value in normalized if value is not None)
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()))
    return tuple(ReferencePatternCount(value=value, count=count) for value, count in ordered)


def _sum_times(values: tuple[MediaTime, ...]) -> MediaTime:
    total = MediaTime(0, 1)
    for value in values:
        total = total + value
    return total


def _media_time_from_fraction(value: Fraction) -> MediaTime:
    return MediaTime(value.numerator, value.denominator)


def _median_time(values: tuple[MediaTime, ...]) -> MediaTime:
    ordered = sorted((value.as_fraction() for value in values))
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return _media_time_from_fraction(ordered[midpoint])
    return _media_time_from_fraction((ordered[midpoint - 1] + ordered[midpoint]) / 2)


def _ref_payload(value: EntityRevisionRef) -> dict[str, object]:
    return {"entity_id": value.entity_id, "revision": value.revision}


def _analysis_ref_payload(value: ShotAnalysisRef) -> dict[str, object]:
    return {
        "shot_ref": _ref_payload(value.shot_ref),
        "analysis_revision": value.revision,
    }


def _time_payload(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _patterns_payload(values: tuple[ReferencePatternCount, ...]) -> list[dict[str, object]]:
    return [{"value": item.value, "count": item.count} for item in values]


def _encode_evidence(evidence: ReferenceStyleEvidence) -> bytes:
    payload = {
        "schema_version": evidence.schema_version,
        "artifact_type": "reference_style_evidence",
        "producer_capability": "preproduction_reference_style",
        "producer_version": REFERENCE_STYLE_EVIDENCE_SCHEMA_VERSION,
        "reference_asset_ref": _ref_payload(evidence.reference_asset_ref),
        "shot_refs": [_ref_payload(value) for value in evidence.shot_refs],
        "analysis_refs": [_analysis_ref_payload(value) for value in evidence.analysis_refs],
        "duration": {
            "total": _time_payload(evidence.total_duration),
            "minimum_shot": _time_payload(evidence.minimum_shot_duration),
            "median_shot": _time_payload(evidence.median_shot_duration),
            "maximum_shot": _time_payload(evidence.maximum_shot_duration),
        },
        "opening": {
            "framing": evidence.opening_framing,
            "camera_motion": evidence.opening_camera_motion,
        },
        "framing_sequence": list(evidence.framing_sequence),
        "camera_motion_sequence": list(evidence.camera_motion_sequence),
        "framing_patterns": _patterns_payload(evidence.framing_patterns),
        "camera_motion_patterns": _patterns_payload(evidence.camera_motion_patterns),
        "action_patterns": _patterns_payload(evidence.action_patterns),
        "subject_patterns": _patterns_payload(evidence.subject_patterns),
        "environment_patterns": _patterns_payload(evidence.environment_patterns),
        "unavailable_dimensions": list(evidence.unavailable_dimensions),
    }
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return serialized.encode("utf-8")


def _seconds(value: MediaTime) -> str:
    return value.to_decimal_seconds_string(fractional_digits=3)


def _patterns_text(values: tuple[ReferencePatternCount, ...]) -> str:
    if not values:
        return "none observed"
    return ", ".join(f"{item.value} ({item.count})" for item in values)


def _planning_guidance(
    evidence: ReferenceStyleEvidence,
    artifact_ref: StoredArtifactRef,
) -> tuple[str, ...]:
    opening_framing = evidence.opening_framing or "unknown"
    opening_motion = evidence.opening_camera_motion or "unknown"
    unavailable = ", ".join(evidence.unavailable_dimensions)
    return (
        "Reference evidence describes abstract technique only; do not copy wording or distinctive "
        "visual expression from the reference.",
        f"Reference evidence artifact: {artifact_ref.artifact_id}.",
        f"Observed {evidence.shot_count} shots; total {_seconds(evidence.total_duration)}s; "
        f"shot cadence min {_seconds(evidence.minimum_shot_duration)}s, median "
        f"{_seconds(evidence.median_shot_duration)}s, max "
        f"{_seconds(evidence.maximum_shot_duration)}s.",
        f"Opening visual pattern: framing={opening_framing}, camera_motion={opening_motion}.",
        f"Observed framing patterns: {_patterns_text(evidence.framing_patterns)}.",
        f"Observed camera-motion patterns: {_patterns_text(evidence.camera_motion_patterns)}.",
        f"Observed action patterns: {_patterns_text(evidence.action_patterns)}.",
        f"Observed subject patterns: {_patterns_text(evidence.subject_patterns)}.",
        f"Unavailable reference dimensions: {unavailable}. Do not infer them from this evidence.",
    )
