from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from video_editing_agent.application.ports.visual_understanding import VisualSemanticsProposal
from video_editing_agent.domain.shot.analysis import NamedQualityScore, VisualSemantics


@dataclass(frozen=True, slots=True)
class ValidatedVisualUnderstanding:
    visual: VisualSemantics
    quality_scores: tuple[NamedQualityScore, ...]


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _text_tuple(values: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return tuple(normalized)


def _quality_scores(proposal: VisualSemanticsProposal) -> tuple[NamedQualityScore, ...]:
    normalized: list[NamedQualityScore] = []
    seen: set[str] = set()
    for score in proposal.quality_scores:
        name = score.name.strip()
        if name in seen:
            continue
        seen.add(name)
        normalized.append(NamedQualityScore(name=name, value=float(score.value)))
    return tuple(normalized)


def normalize_visual_semantics_proposal(proposal: VisualSemanticsProposal) -> VisualSemantics:
    """Deterministically normalize provider proposal text before any ShotAnalysis commit."""
    return VisualSemantics(
        summary=_optional_text(proposal.summary),
        tags=_text_tuple(proposal.tags),
        subjects=_text_tuple(proposal.subjects),
        actions=_text_tuple(proposal.actions),
        environment=_optional_text(proposal.environment),
        framing=_optional_text(proposal.framing),
        camera_motion=_optional_text(proposal.camera_motion),
    )


def normalize_visual_understanding_proposal(
    proposal: VisualSemanticsProposal,
) -> ValidatedVisualUnderstanding:
    """Validate semantics and visual-quality dimensions before owner commit."""
    return ValidatedVisualUnderstanding(
        visual=normalize_visual_semantics_proposal(proposal),
        quality_scores=_quality_scores(proposal),
    )
