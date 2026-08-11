from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from video_editing_agent.application.ports.preproduction_planning import (
    PlanningPolicyGuidance,
    ScriptPlanProposal,
)
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.script.model import ScriptPlan


@dataclass(frozen=True, slots=True)
class ScriptProposalViolation:
    code: str
    reason: str
    section_id: str | None = None
    excerpt: str | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("violation code must not be empty")
        if not self.reason.strip():
            raise ValueError("violation reason must not be empty")
        if self.section_id is not None and not self.section_id.strip():
            raise ValueError("violation section_id must not be empty when provided")
        if self.excerpt is not None and not self.excerpt.strip():
            raise ValueError("violation excerpt must not be empty when provided")


@dataclass(frozen=True, slots=True)
class ScriptProposalReview:
    accepted: bool
    violations: tuple[ScriptProposalViolation, ...] = ()

    def __post_init__(self) -> None:
        if self.accepted and self.violations:
            raise ValueError("accepted Script proposal review cannot contain violations")
        if not self.accepted and not self.violations:
            raise ValueError("rejected Script proposal review must contain at least one violation")


@dataclass(frozen=True, slots=True)
class ScriptProposalReviewRequest:
    brief: Brief
    proposal: ScriptPlanProposal
    current_script: ScriptPlan | None = None
    instruction: str | None = None
    policy_guidance: PlanningPolicyGuidance | None = None


class ScriptProposalReviewPort(Protocol):
    """Replaceable semantic reviewer that may veto but never mutate a Script proposal."""

    def review(self, request: ScriptProposalReviewRequest) -> ScriptProposalReview: ...
