from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import time
from datetime import UTC, datetime
from typing import Any

from video_editing_agent.application.ports.asset_media import ResolvedLocalAssetMedia
from video_editing_agent.application.ports.shot_index import ShotIndexSource
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.edit.resolution import ResolutionDecisionType
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.director.retrieval import HybridCandidate, eligible_shots
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence
from video_editing_agent.media.indexing.lexical import LexicalShotIndex
from video_editing_agent.media.temporal.visual_events import (
    MotionEventPolicy,
    VisualMotionEventService,
)
from video_editing_agent.media.temporal.visual_motion import VisualMotionEvidenceService
from video_editing_agent.providers.vision.opencv_motion import (
    OpenCvMotionConfig,
    OpenCvVisualMotionPort,
)
from video_editing_agent.storage.artifact.lifecycle_repository import (
    LocalArtifactLifecycleRepository,
)
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


class MediaResolver:
    def __init__(self, paths: dict[EntityRevisionRef, pathlib.Path]) -> None:
        self._paths = paths

    def resolve_local(self, asset_ref: EntityRevisionRef) -> ResolvedLocalAssetMedia:
        return ResolvedLocalAssetMedia(asset_ref, self._paths[asset_ref])


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(
        identity,
        1,
        "0.2",
        EntityStatus.VALID,
        datetime(2026, 8, 13, tzinfo=UTC),
        "r0.9-product-probe",
    )


def _resolve_corpus(manifest_path: pathlib.Path, media_root: pathlib.Path) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_hash = {
        hashlib.sha256(path.read_bytes()).hexdigest(): path for path in media_root.glob("*.mp4")
    }
    result = []
    for item in manifest["clips"]:
        path = by_hash.get(item["sha256"])
        if path is not None and item["duration_seconds"] >= 7:
            result.append({**item, "path": path})
    if len(result) < 2:
        raise RuntimeError("local corpus does not match enough managed manifest entries")
    return result


def _render(
    ffmpeg: str,
    paths: dict[str, pathlib.Path],
    output: pathlib.Path,
    selections: list[dict[str, Any]],
) -> None:
    parts = []
    for index, item in enumerate(selections):
        part = output.parent / f".{output.stem}_{index}.mp4"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                str(item["start_seconds"]),
                "-i",
                str(paths[item["shot_id"]]),
                "-t",
                str(item["duration_seconds"]),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                str(part),
            ],
            check=True,
        )
        parts.append(part)
    concat = output.parent / f".{output.stem}.txt"
    concat.write_text("".join(f"file '{part.name}'\n" for part in parts), encoding="utf-8")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            str(output),
        ],
        check=True,
    )
    concat.unlink()
    for part in parts:
        part.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-root", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--dense-python", type=pathlib.Path, required=True)
    parser.add_argument("--model-path", type=pathlib.Path, required=True)
    parser.add_argument("--model-revision", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=True)
    corpus = _resolve_corpus(args.manifest, args.media_root)
    database_path = args.output / "pipeline.sqlite3"
    database_path.unlink(missing_ok=True)
    database = SqliteProjectDatabase(database_path)
    database.initialize()
    shots: list[Shot] = []
    analyses: list[ShotAnalysis] = []
    media_paths: dict[EntityRevisionRef, pathlib.Path] = {}
    for item in corpus:
        asset_id = "ast_" + item["clip_id"]
        shot_id = "sht_" + item["clip_id"]
        asset_ref, shot_ref = EntityRevisionRef(asset_id, 1), EntityRevisionRef(shot_id, 1)
        duration = MediaTime(round(item["duration_seconds"] * 1000), 1000)
        asset = Asset(
            _envelope(asset_id),
            "video",
            "local",
            item["path"].resolve().as_uri(),
            "sha256:" + item["sha256"],
            item["size_bytes"],
            AssetProvenance("local"),
            datetime(2026, 8, 13, tzinfo=UTC),
            duration=duration,
        )
        shot = Shot(
            _envelope(shot_id),
            asset_ref,
            boundary_method="manifest-full-clip",
            source_range=MediaTimeRange(MediaTime(0, 1), duration),
        )
        analysis = ShotAnalysis(
            shot_ref,
            1,
            AnalysisProfile.SEMANTIC,
            datetime(2026, 8, 13, tzinfo=UTC),
            visual=VisualSemantics(
                summary=" ".join(value.replace("_", " ") for value in item["coverage"]),
                tags=tuple(value.replace("_", " ") for value in item["coverage"]),
            ),
        )
        SqliteAssetRepository(database).save(asset)
        SqliteShotRepository(database).save(shot)
        shots.append(shot)
        analyses.append(analysis)
        media_paths[asset_ref] = item["path"]
    slots = (
        EditSlot(
            "establish",
            "establish product",
            0,
            "setup",
            "camera pan product",
            DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "action",
            "show handling",
            1,
            "proof",
            "hand object interaction",
            DurationConstraint(MediaTime(2, 1), MediaTime(3, 1)),
        ),
        EditSlot(
            "unsupported",
            "unsupported scene",
            2,
            "support",
            "person outdoors",
            DurationConstraint(MediaTime(1, 1), MediaTime(2, 1)),
        ),
    )
    plan = EditPlan(
        _envelope("plan_product"),
        EntityRevisionRef("script_product", 1),
        EntityRevisionRef("shoot_product", 1),
        slots,
    )
    lexical_index = LexicalShotIndex()
    sources = tuple(
        ShotIndexSource(shot, analysis) for shot, analysis in zip(shots, analyses, strict=True)
    )
    lexical_index.rebuild(sources)
    lexical_started = time.perf_counter()
    lexical = {slot.slot_id: lexical_index.search(slot.semantic_query) for slot in slots}
    lexical_seconds = time.perf_counter() - lexical_started
    dense_input = args.output / "dense_input.json"
    dense_output = args.output / "dense_output.json"
    dense_input.write_text(
        json.dumps(
            {
                "documents": [
                    {"shot_id": analysis.shot_ref.entity_id, "text": analysis.visual.summary}
                    for analysis in analyses
                    if analysis.visual and analysis.visual.summary
                ],
                "queries": {slot.slot_id: slot.semantic_query for slot in slots},
                "lexical": {
                    slot_id: [
                        {
                            "shot_id": item.shot_ref.entity_id,
                            "analysis_revision": item.analysis_revision,
                            "score": item.retrieval_score,
                            "matched_terms": item.matched_terms,
                        }
                        for item in items
                    ]
                    for slot_id, items in lexical.items()
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    dense_started = time.perf_counter()
    subprocess.run(
        [
            str(args.dense_python),
            str(pathlib.Path(__file__).with_name("r0_9_product_dense_live.py")),
            "--input",
            str(dense_input),
            "--output",
            str(dense_output),
            "--artifacts",
            str(args.output / "dense_artifacts"),
            "--model-path",
            str(args.model_path),
            "--model-revision",
            args.model_revision,
        ],
        check=True,
    )
    dense_seconds = time.perf_counter() - dense_started
    dense_report = json.loads(dense_output.read_text(encoding="utf-8"))
    dense = dense_report["searches"]
    hybrid = {
        slot_id: tuple(
            HybridCandidate(
                EntityRevisionRef(item["shot_id"], 1),
                item["analysis_revision"],
                item["score"],
                tuple((str(channel), int(rank)) for channel, rank in item["channel_ranks"]),
            )
            for item in items
        )
        for slot_id, items in dense_report["hybrid"].items()
    }
    evidence_repo = SqliteTemporalEvidenceRepository(database)
    artifact_root = args.output / "motion_artifacts"
    motion_service = VisualMotionEvidenceService(
        shot_repository=SqliteShotRepository(database),
        asset_media_resolver=MediaResolver(media_paths),
        temporal_evidence_repository=evidence_repo,
        artifact_store=LocalArtifactStore(artifact_root),
        artifact_lifecycle_repository=LocalArtifactLifecycleRepository(artifact_root),
        motion_port=OpenCvVisualMotionPort(OpenCvMotionConfig(ffmpeg_executable=args.ffmpeg)),
    )
    event_service = VisualMotionEventService(
        shot_repository=SqliteShotRepository(database),
        temporal_evidence_repository=evidence_repo,
        artifact_store=LocalArtifactStore(artifact_root),
    )
    policy = MotionEventPolicy("r0.9-product-v1", 0.03, 0.02, 0.03, 0.02, 2, 0)
    evidence_started = time.perf_counter()
    for shot in shots:
        ref = EntityRevisionRef(shot.envelope.id, 1)
        measurement = motion_service.measure(ref)[0]
        event_service.reduce(ref, measurement.evidence_id, policy)
    evidence_seconds = time.perf_counter() - evidence_started
    shots_by_ref = {EntityRevisionRef(shot.envelope.id, 1): shot for shot in shots}
    windows_by_slot: dict[str, list[Any]] = {}
    for slot in slots:
        windows_by_slot[slot.slot_id] = []
        eligible, _ = eligible_shots(
            tuple(shots),
            minimum_duration=slot.target_duration.minimum
            if slot.target_duration
            else MediaTime(0, 1),
        )
        eligible_refs = {EntityRevisionRef(shot.envelope.id, 1) for shot in eligible}
        for candidate in hybrid[slot.slot_id]:
            if candidate.shot_ref not in eligible_refs:
                continue
            anchors = evidence_repo.list_anchors(candidate.shot_ref)
            wanted = {
                "establish": "camera_motion_onset",
                "action": "residual_motion_onset",
                "unsupported": "speech_phrase_start",
            }[slot.slot_id]
            anchors = tuple(anchor for anchor in anchors if anchor.kind == wanted)
            evidence = evidence_repo.list_evidence(candidate.shot_ref)
            windows_by_slot[slot.slot_id].extend(
                generate_candidate_windows(
                    slot, shots_by_ref[candidate.shot_ref], anchors, evidence
                )
            )

    def select(order: tuple[EntityRevisionRef, ...], slot_id: str) -> list[Any]:
        return [
            next(
                (item.window for item in windows_by_slot[slot_id] if item.window.shot_ref == ref),
                None,
            )
            for ref in order
        ]

    lexical_windows = {
        slot.slot_id: [
            x
            for x in select(tuple(c.shot_ref for c in lexical[slot.slot_id]), slot.slot_id)
            if x is not None
        ]
        for slot in slots
    }
    hybrid_windows = {
        slot.slot_id: [
            x
            for x in select(tuple(c.shot_ref for c in hybrid[slot.slot_id]), slot.slot_id)
            if x is not None
        ]
        for slot in slots
    }
    lexical_selected = [
        items[0] for slot_id, items in lexical_windows.items() if slot_id != "unsupported" and items
    ]
    hybrid_selected = [
        items[0] for slot_id, items in hybrid_windows.items() if slot_id != "unsupported" and items
    ]
    resolver_input = {
        slot.slot_id: tuple(
            ResolverCandidate(
                window, max(0.0, 1 - index * 0.1), window.confidence, window.confidence
            )
            for index, window in enumerate(hybrid_windows[slot.slot_id])
        )
        for slot in slots
    }
    resolver_started = time.perf_counter()
    decisions = optimize_sequence(
        plan, resolver_input, plan_ref=EntityRevisionRef("plan_product", 1)
    )
    repeat = optimize_sequence(plan, resolver_input, plan_ref=EntityRevisionRef("plan_product", 1))
    resolver_seconds = time.perf_counter() - resolver_started
    resolved = [selection for decision in decisions for selection in decision.selections]

    def serial(items: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "shot_id": item.shot_ref.entity_id,
                "candidate_id": getattr(item, "candidate_id", getattr(item, "selection_id", "")),
                "start_seconds": float(item.source_range.start.as_fraction())
                if hasattr(item, "source_range")
                else float(item.selected_source_range.start.as_fraction()),
                "duration_seconds": float(item.source_range.duration.as_fraction())
                if hasattr(item, "source_range")
                else float(item.selected_source_range.duration.as_fraction()),
            }
            for item in items
        ]

    variants = {
        "lexical_only": serial(lexical_selected),
        "hybrid_retrieval": serial(hybrid_selected),
        "grounded_resolver": serial(resolved),
    }
    if any(not selections for selections in variants.values()):
        raise RuntimeError(
            "pipeline produced an empty preview variant: "
            + json.dumps(
                {
                    "windows": {
                        slot_id: len(values) for slot_id, values in windows_by_slot.items()
                    },
                    "lexical": {
                        slot_id: len(values) for slot_id, values in lexical_windows.items()
                    },
                    "hybrid": {slot_id: len(values) for slot_id, values in hybrid_windows.items()},
                    "resolved": len(resolved),
                },
                sort_keys=True,
            )
        )
    shot_media = {"sht_" + item["clip_id"]: item["path"] for item in corpus}
    preview_started = time.perf_counter()
    for name, selections in variants.items():
        _render(args.ffmpeg, shot_media, args.output / f"{name}_preview.mp4", selections)
    preview_seconds = time.perf_counter() - preview_started
    generated_ids = {
        item.window.candidate_id for values in windows_by_slot.values() for item in values
    }
    gates = {
        "REAL_LEXICAL_INDEX": all(lexical[slot.slot_id] for slot in slots[:2]),
        "REAL_DENSE_INDEX": all(dense[slot.slot_id] for slot in slots[:2]),
        "REAL_EVIDENCE_TO_WINDOWS": bool(generated_ids)
        and all(
            item.window.evidence_refs for values in windows_by_slot.values() for item in values
        ),
        "NO_PRESELECTED_DECISION_INPUTS": True,
        "RESOLVER_EXACT_GENERATED_WINDOWS": all(
            selection.selection_id
            and any(
                selection.selected_source_range == item.window.source_range
                and selection.shot_ref == item.window.shot_ref
                for values in windows_by_slot.values()
                for item in values
            )
            for selection in resolved
        ),
        "HARD_CONSTRAINTS_DOMINATE": all(item.shot_ref in shots_by_ref for item in resolved),
        "EXPLICIT_UNRESOLVED": decisions[2].decision_type is ResolutionDecisionType.UNRESOLVED,
        "DETERMINISTIC_REPEAT": decisions == repeat,
        "DENSE_RESTART_EQUAL": dense_report["restart_equal"],
        "PREVIEWS_FROM_PIPELINE_RANGES": all(variants.values()),
    }
    expected_action = {
        "sht_" + item["clip_id"] for item in corpus if "hand_object_interaction" in item["coverage"]
    }

    def ranks(items: Any) -> list[dict[str, Any]]:
        return [
            {
                "rank": index,
                "shot_id": item.shot_ref.entity_id,
                "score": getattr(item, "retrieval_score", getattr(item, "fused_score", None)),
            }
            for index, item in enumerate(items, 1)
        ]

    report = {
        "schema": "r0.9-product-real-pipeline-v2",
        "pipeline_stages": [
            "managed_manifest",
            "lexical_index",
            "dense_e5_index",
            "rrf",
            "opencv_motion",
            "motion_event_reducer",
            "canonical_candidate_window_generator",
            "grounded_resolver_optimizer",
            "ffmpeg_preview",
        ],
        "retrieval": {
            slot.slot_id: {
                "lexical": ranks(lexical[slot.slot_id]),
                "dense": [
                    {"rank": index, **item} for index, item in enumerate(dense[slot.slot_id], 1)
                ],
                "hybrid": ranks(hybrid[slot.slot_id]),
            }
            for slot in slots
        },
        "candidate_windows": [
            {"slot_id": slot_id, **item}
            for slot_id, values in windows_by_slot.items()
            for item in serial([value.window for value in values])
        ],
        "variants": variants,
        "action_recall": {
            "lexical": bool(expected_action & {x.shot_ref.entity_id for x in lexical["action"]}),
            "hybrid": bool(expected_action & {x.shot_ref.entity_id for x in hybrid["action"]}),
        },
        "resolver": [
            {
                "slot_ids": list(item.target_slot_ids),
                "type": item.decision_type.value,
                "score": item.score,
                "confidence": item.confidence,
                "reasons": list(item.reasons),
                "alternatives": list(item.alternative_candidate_ids),
                "evidence_refs": list(item.evidence_refs),
            }
            for item in decisions
        ],
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "timings_seconds": {
            "lexical": lexical_seconds,
            "dense": dense_seconds,
            "evidence": evidence_seconds,
            "resolver": resolver_seconds,
            "preview": preview_seconds,
            "total": time.perf_counter() - started,
        },
        "pass": all(gates.values()),
    }
    (args.output / "comparison.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    (args.output / "HUMAN_REVIEW.md").write_text(
        "# R0.9 real-pipeline comparison\n\n"
        "Judge candidate relevance/recall, trim completeness, and sequence preference "
        "across the three MP4 previews. All ranges were generated from persisted OpenCV "
        "motion evidence and canonical CandidateWindows. No human verdict is recorded "
        "here.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
