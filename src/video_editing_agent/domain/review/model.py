from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTimeRange


class ReviewStage(StrEnum):
    PLAN = "plan"
    RESOLUTION = "resolution"
    TIMELINE_VALIDATION = "timeline_validation"
    PROXY_EDITORIAL_AV = "proxy_editorial_av"
    FINAL_TECHNICAL_QC = "final_technical_qc"


class FindingSeverity(StrEnum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    BLOCKING = "blocking"


@dataclass(frozen=True, slots=True)
class ReviewFinding:
    finding_id: str
    severity: FindingSeverity
    problem: str
    recommended_action: str
    affected_owner: str
    affected_slot_ids: tuple[str, ...] = ()
    source_range: MediaTimeRange | None = None
    timeline_range: MediaTimeRange | None = None
    evidence_refs: tuple[str, ...] = ()
    requires_new_analysis: bool = False
    affected_downstream: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("finding_id", self.finding_id),
            ("problem", self.problem),
            ("recommended_action", self.recommended_action),
            ("affected_owner", self.affected_owner),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if not isinstance(self.requires_new_analysis, bool):
            raise TypeError("requires_new_analysis must be a bool")


@dataclass(frozen=True, slots=True)
class ReviewReport:
    envelope: EntityEnvelope
    stage: ReviewStage
    target_ref: EntityRevisionRef
    passed: bool
    findings: tuple[ReviewFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a bool")
        if self.passed and any(
            finding.severity is FindingSeverity.BLOCKING for finding in self.findings
        ):
            raise ValueError("passed ReviewReport cannot contain blocking findings")


class ReviewDisposition(StrEnum):
    PASS = "pass"
    CORRECTION_REQUIRED = "correction_required"
    BLOCKED = "blocked"


class ReviewCorrectionRoute(StrEnum):
    NONE = "none"
    RERENDER_SAME_EDL = "rerender_same_edl"
    RETURN_TO_AUDIO_EDITORIAL = "return_to_audio_editorial"
    ESCALATE_OWNER = "escalate_owner"


@dataclass(frozen=True, slots=True)
class ReviewVerdict:
    disposition: ReviewDisposition
    report: ReviewReport
    correction_route: ReviewCorrectionRoute
    repair_attempt: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.repair_attempt, bool)
            or not isinstance(self.repair_attempt, int)
            or self.repair_attempt < 0
        ):
            raise ValueError("repair_attempt must be a non-negative int")
        if self.disposition is ReviewDisposition.PASS:
            if not self.report.passed:
                raise ValueError("PASS verdict requires a passed ReviewReport")
            if self.correction_route is not ReviewCorrectionRoute.NONE:
                raise ValueError("PASS verdict cannot carry a correction route")
        elif self.disposition is ReviewDisposition.CORRECTION_REQUIRED:
            if self.report.passed:
                raise ValueError("CORRECTION_REQUIRED verdict requires a failed ReviewReport")
            if self.correction_route in {
                ReviewCorrectionRoute.NONE,
                ReviewCorrectionRoute.ESCALATE_OWNER,
            }:
                raise ValueError("CORRECTION_REQUIRED verdict requires an executable owner route")
        else:
            if self.report.passed:
                raise ValueError("BLOCKED verdict requires a failed ReviewReport")
            if self.correction_route is not ReviewCorrectionRoute.ESCALATE_OWNER:
                raise ValueError("BLOCKED verdict must escalate instead of auto-repairing")
