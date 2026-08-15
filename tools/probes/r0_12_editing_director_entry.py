from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from video_editing_agent.application.ports.director import (
    DirectorProposal,
    DirectorRequest,
    EditSlotProposal,
)
from video_editing_agent.application.use_cases.editing_director import GenerateEditPlanRequest
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.edit.resolution import ResolutionDecisionType
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence
from video_editing_agent.storage.project.workspace import ProjectWorkspace

NOW = datetime(2026, 8, 15, tzinfo=UTC)


def _envelope(identity: str) -> EntityEnvelope:
    return EntityEnvelope(identity, 1, "0.2", EntityStatus.VALID, NOW, "r0.12-director-probe")


class DeterministicDirector:
    def __init__(self) -> None:
        self.request: DirectorRequest | None = None

    def propose(self, request: DirectorRequest) -> DirectorProposal:
        self.request = request
        return DirectorProposal(
            (
                EditSlotProposal(
                    "proof",
                    0,
                    "proof",
                    "show grounded pouring proof",
                    "bottle pour",
                    MediaTime(1, 1),
                    MediaTime(1, 1),
                    "quick",
                    importance=3,
                ),
            )
        )


def _asset(identity: str, role: AssetUsageRole) -> Asset:
    return Asset(
        _envelope(identity),
        "video",
        "local",
        f"file:///{identity}.mp4",
        f"sha256:{identity}",
        10,
        AssetProvenance("local"),
        NOW,
        duration=MediaTime(4, 1),
        usage_role=role,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="r0_12_director_") as directory:
        root = Path(directory)
        workspace = ProjectWorkspace.open(root)
        brief = Brief(_envelope("brief"), "Bottle", "Sell", "buyers", "short", "Bottle proof")
        workspace.briefs.save(brief)
        for identity, role in (
            ("editable", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE),
            ("reference", AssetUsageRole.REFERENCE_ANALYSIS_ONLY),
        ):
            asset = _asset(identity, role)
            shot_id = f"shot-{identity}"
            workspace.assets.save(asset)
            workspace.shots.save(
                Shot(
                    _envelope(shot_id),
                    EntityRevisionRef(identity, 1),
                    source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
                    boundary_method="probe",
                )
            )
            workspace.analyses.save(
                ShotAnalysis(
                    EntityRevisionRef(shot_id, 1),
                    1,
                    AnalysisProfile.SEMANTIC,
                    NOW,
                    visual=VisualSemantics(
                        "bottle pour proof", ("bottle", "pour"), ("bottle",), ("pour",)
                    ),
                )
            )
        director = DeterministicDirector()
        plan = workspace.editing_runtime(director=director).editing.generate_edit_plan(
            GenerateEditPlanRequest("edit-plan", EntityRevisionRef("brief", 1))
        )
        reopened = ProjectWorkspace.open(root)
        persisted = reopened.edit_plans.load(EntityRevisionRef("edit-plan", 1))
        reopened.rebuild_index()
        retrieved = reopened.shot_index.search(plan.slots[0].semantic_query)
        shot = reopened.shots.load(EntityRevisionRef("shot-editable", 1))
        evidence = TemporalEvidence("evidence", retrieved[0].shot_ref, "motion", "probe", "1", 1.0)
        anchor = TemporalAnchor(
            "anchor", retrieved[0].shot_ref, "onset", MediaTime(1, 1), 1.0, ("evidence",), "probe"
        )
        windows = generate_candidate_windows(plan.slots[0], shot, (anchor,), (evidence,))
        decisions = optimize_sequence(
            plan,
            {"proof": tuple(ResolverCandidate(item.window, 1.0, 1.0, 1.0) for item in windows)},
            plan_ref=EntityRevisionRef("edit-plan", 1),
        )
        gates = {
            "editing_only_no_fabricated_planning": plan.script_plan_ref is None
            and plan.shooting_plan_ref is None,
            "reference_only_excluded": director.request is not None
            and tuple(item.shot_ref.entity_id for item in director.request.footage)
            == ("shot-editable",),
            "persisted_restart_equality": persisted == plan,
            "existing_retrieval_grounded": retrieved[0].shot_ref
            == EntityRevisionRef("shot-editable", 1),
            "canonical_candidate_window": len(windows) == 1,
            "existing_resolver_resolved": decisions[0].decision_type
            is ResolutionDecisionType.RESOLVED,
        }
        print(
            json.dumps(
                {"status": "PASS" if all(gates.values()) else "FAIL", "gates": gates}, indent=2
            )
        )
        return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
