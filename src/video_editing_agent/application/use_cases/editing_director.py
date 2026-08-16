from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from video_editing_agent.application.ports.asset_repository import AssetRepository
from video_editing_agent.application.ports.brief_repository import BriefRepository
from video_editing_agent.application.ports.director import (
    DirectorFootageEvidence,
    DirectorPort,
    DirectorRequest,
)
from video_editing_agent.application.ports.edit_plan_repository import EditPlanRepository
from video_editing_agent.application.ports.script_plan_repository import ScriptPlanRepository
from video_editing_agent.application.ports.shooting_plan_repository import ShootingPlanRepository
from video_editing_agent.application.ports.shot_analysis_repository import ShotAnalysisRepository
from video_editing_agent.application.ports.shot_repository import ShotRepository
from video_editing_agent.domain.asset.model import Asset
from video_editing_agent.domain.asset.policy import is_visual_resolver_eligible
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.edit.model import DurationConstraint, EditPlan, EditSlot
from video_editing_agent.domain.shot.analysis import ShotAnalysis
from video_editing_agent.domain.shot.model import Shot


def _duration_constraint(
    minimum: MediaTime | None, maximum: MediaTime | None
) -> DurationConstraint | None:
    if minimum is None and maximum is None:
        return None
    if minimum is None or maximum is None:
        raise ValueError("Director duration bounds must be both provided or both omitted")
    return DurationConstraint(minimum, maximum)


class AssetCatalog(AssetRepository, Protocol):
    def list_all(self) -> tuple[Asset, ...]: ...


class ShotCatalog(ShotRepository, Protocol):
    def list_all(self) -> tuple[Shot, ...]: ...


class AnalysisCatalog(ShotAnalysisRepository, Protocol):
    def list_latest(self) -> tuple[ShotAnalysis, ...]: ...


@dataclass(frozen=True, slots=True)
class GenerateEditPlanRequest:
    edit_plan_id: str
    brief_ref: EntityRevisionRef
    script_plan_ref: EntityRevisionRef | None = None
    shooting_plan_ref: EntityRevisionRef | None = None
    policy_guidance: tuple[str, ...] = ()
    created_by: str = "editing-director"

    def __post_init__(self) -> None:
        if not self.edit_plan_id.strip() or not self.created_by.strip():
            raise ValueError("edit_plan_id and created_by must not be empty")
        if self.shooting_plan_ref is not None and self.script_plan_ref is None:
            raise ValueError("ShootingPlan context requires ScriptPlan context")


class EditingDirectorWorkflow:
    def __init__(
        self,
        *,
        briefs: BriefRepository,
        scripts: ScriptPlanRepository,
        shooting_plans: ShootingPlanRepository,
        assets: AssetCatalog,
        shots: ShotCatalog,
        analyses: AnalysisCatalog,
        edit_plans: EditPlanRepository,
        director: DirectorPort,
    ) -> None:
        self._briefs = briefs
        self._scripts = scripts
        self._shooting = shooting_plans
        self._assets = assets
        self._shots = shots
        self._analyses = analyses
        self._edit_plans = edit_plans
        self._director = director

    def generate(self, request: GenerateEditPlanRequest) -> EditPlan:
        brief = self._briefs.load(request.brief_ref)
        script = (
            None if request.script_plan_ref is None else self._scripts.load(request.script_plan_ref)
        )
        shooting = (
            None
            if request.shooting_plan_ref is None
            else self._shooting.load(request.shooting_plan_ref)
        )
        director_request = DirectorRequest(
            brief,
            self._eligible_footage(),
            script,
            shooting,
            request.policy_guidance,
        )
        proposal = self._director.propose(director_request)
        slots = tuple(
            EditSlot(
                item.slot_id,
                item.purpose,
                item.order,
                item.narrative_role,
                item.semantic_query,
                _duration_constraint(item.minimum_duration, item.maximum_duration),
                item.pacing,
                item.continuity_hint,
                item.allow_reuse,
                item.importance,
            )
            for item in sorted(proposal.slots, key=lambda value: (value.order, value.slot_id))
        )
        revision = (self._edit_plans.latest_revision(request.edit_plan_id) or 0) + 1
        derived = tuple(
            value
            for value in (request.brief_ref, request.script_plan_ref, request.shooting_plan_ref)
            if value is not None
        )
        plan = EditPlan(
            EntityEnvelope(
                request.edit_plan_id,
                revision,
                "0.2",
                EntityStatus.VALID,
                datetime.now(UTC),
                request.created_by,
                derived,
            ),
            request.script_plan_ref,
            request.shooting_plan_ref,
            slots,
            brief_ref=request.brief_ref,
        )
        self._edit_plans.save(plan)
        return plan

    def _eligible_footage(self) -> tuple[DirectorFootageEvidence, ...]:
        latest_assets: dict[str, Asset] = {}
        for asset in self._assets.list_all():
            current = latest_assets.get(asset.envelope.id)
            if current is None or asset.envelope.revision > current.envelope.revision:
                latest_assets[asset.envelope.id] = asset
        assets = {
            EntityRevisionRef(value.envelope.id, value.envelope.revision): value
            for value in latest_assets.values()
            if value.envelope.status is EntityStatus.VALID
            and is_visual_resolver_eligible(
                media_kind=value.media_kind,
                origin=value.origin,
                usage_role=value.usage_role,
            )
        }
        shots = {
            EntityRevisionRef(value.envelope.id, value.envelope.revision): value
            for value in self._shots.list_all()
            if value.envelope.status is EntityStatus.VALID and value.asset_ref in assets
        }
        evidence = []
        for analysis in self._analyses.list_latest():
            shot = shots.get(analysis.shot_ref)
            if shot is None:
                continue
            visual = analysis.visual
            evidence.append(
                DirectorFootageEvidence(
                    analysis.shot_ref,
                    shot.asset_ref,
                    analysis.revision,
                    analysis.profile,
                    None if visual is None else visual.summary,
                    () if visual is None else visual.tags,
                    () if visual is None else visual.subjects,
                    () if visual is None else visual.actions,
                )
            )
        evidence.sort(key=lambda value: (value.shot_ref.entity_id, value.shot_ref.revision))
        return tuple(evidence)
