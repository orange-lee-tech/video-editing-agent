from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from video_editing_agent.application.ports.director import (
    DirectorFootageEvidence,
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
from video_editing_agent.domain.script.model import ScriptPlan
from video_editing_agent.domain.shooting.model import ShootingPlan
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.editing.director.candidate_windows import generate_candidate_windows
from video_editing_agent.editing.resolver.optimizer import ResolverCandidate, optimize_sequence
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekPlanningResponseError,
)
from video_editing_agent.providers.llm.deepseek_director import DeepSeekDirectorPort
from video_editing_agent.storage.project.workspace import ProjectWorkspace
from video_editing_agent.storage.repositories.edit_plan_codec import (
    decode_edit_plan,
    encode_edit_plan,
)
from video_editing_agent.storage.repositories.sqlite_repositories import RevisionConflictError

NOW = datetime(2026, 8, 15, tzinfo=UTC)


def _envelope(identity: str, revision: int = 1) -> EntityEnvelope:
    return EntityEnvelope(identity, revision, "0.2", EntityStatus.VALID, NOW, "test")


class FixedDirector:
    def __init__(self) -> None:
        self.requests: list[DirectorRequest] = []

    def propose(self, request: DirectorRequest) -> DirectorProposal:
        self.requests.append(request)
        return DirectorProposal(
            (
                EditSlotProposal(
                    "proof",
                    0,
                    "proof",
                    "show the bottle pour",
                    "bottle pour",
                    MediaTime(1, 1),
                    MediaTime(1, 1),
                    "quick",
                    importance=3,
                ),
            )
        )


def _brief(identity: str = "brief") -> Brief:
    return Brief(_envelope(identity), "Title", "Sell", "buyers", "short", "Bottle proof")


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


def _seed(workspace: ProjectWorkspace) -> tuple[Brief, Shot, ShotAnalysis]:
    brief = _brief()
    workspace.briefs.save(brief)
    editable = _asset("editable", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    reference = _asset("reference", AssetUsageRole.REFERENCE_ANALYSIS_ONLY)
    workspace.assets.save(editable)
    workspace.assets.save(reference)
    shots = []
    analyses = []
    for identity, asset in (("shot-editable", editable), ("shot-reference", reference)):
        shot = Shot(
            _envelope(identity),
            EntityRevisionRef(asset.envelope.id, 1),
            source_range=MediaTimeRange(MediaTime(0, 1), MediaTime(4, 1)),
            boundary_method="test",
        )
        analysis = ShotAnalysis(
            EntityRevisionRef(identity, 1),
            1,
            AnalysisProfile.SEMANTIC,
            NOW,
            visual=VisualSemantics("bottle pour proof", ("bottle", "pour"), ("bottle",), ("pour",)),
        )
        workspace.shots.save(shot)
        workspace.analyses.save(analysis)
        shots.append(shot)
        analyses.append(analysis)
    return brief, shots[0], analyses[0]


def test_editing_only_generates_persists_and_enters_existing_resolver(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path)
    brief, shot, _ = _seed(workspace)
    director = FixedDirector()

    runtime = workspace.editing_runtime(director=director)
    plan = runtime.editing.generate_edit_plan(
        GenerateEditPlanRequest("edit-plan", EntityRevisionRef(brief.envelope.id, 1))
    )

    assert plan.script_plan_ref is None and plan.shooting_plan_ref is None
    assert workspace.edit_plans.load(EntityRevisionRef("edit-plan", 1)) == plan
    assert len(director.requests[0].footage) == 1
    assert director.requests[0].footage[0].shot_ref.entity_id == "shot-editable"
    workspace.rebuild_index()
    retrieved = workspace.shot_index.search(plan.slots[0].semantic_query)
    assert retrieved[0].shot_ref == EntityRevisionRef(shot.envelope.id, 1)
    evidence = TemporalEvidence("evidence", retrieved[0].shot_ref, "motion", "test", "1", 1.0)
    anchor = TemporalAnchor(
        "anchor", retrieved[0].shot_ref, "onset", MediaTime(1, 1), 1.0, ("evidence",), "test"
    )
    windows = generate_candidate_windows(plan.slots[0], shot, (anchor,), (evidence,))
    decisions = optimize_sequence(
        plan,
        {"proof": tuple(ResolverCandidate(item.window, 1.0, 1.0, 1.0) for item in windows)},
        plan_ref=EntityRevisionRef("edit-plan", 1),
    )
    assert decisions[0].decision_type is ResolutionDecisionType.RESOLVED


def test_combined_mode_preserves_exact_planning_lineage(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path)
    brief, _, _ = _seed(workspace)
    brief_ref = EntityRevisionRef(brief.envelope.id, 1)
    script = ScriptPlan(_envelope("script"), brief_ref)
    shooting = ShootingPlan(_envelope("shooting"), EntityRevisionRef("script", 1), ())
    workspace.scripts.save(script)
    workspace.shooting_plans.save(shooting)
    director = FixedDirector()

    plan = workspace.editing_runtime(director=director).editing.generate_edit_plan(
        GenerateEditPlanRequest(
            "combined", brief_ref, EntityRevisionRef("script", 1), EntityRevisionRef("shooting", 1)
        )
    )

    assert plan.brief_ref == brief_ref
    assert plan.script_plan_ref == EntityRevisionRef("script", 1)
    assert plan.shooting_plan_ref == EntityRevisionRef("shooting", 1)
    assert director.requests[0].script_plan == script
    assert director.requests[0].shooting_plan == shooting


def test_lineage_and_missing_footage_fail_closed() -> None:
    brief = _brief()
    evidence = DirectorFootageEvidence(
        EntityRevisionRef("shot", 1),
        EntityRevisionRef("asset", 1),
        1,
        AnalysisProfile.SEMANTIC,
        "summary",
        (),
        (),
        (),
    )
    mismatched_script = ScriptPlan(_envelope("script"), EntityRevisionRef("other", 1))
    valid_script = ScriptPlan(_envelope("valid-script"), EntityRevisionRef("brief", 1))
    mismatched_shooting = ShootingPlan(
        _envelope("shooting"), EntityRevisionRef("other-script", 1), ()
    )
    with pytest.raises(ValueError, match="eligible analyzed"):
        DirectorRequest(brief, ())
    with pytest.raises(ValueError, match="exact Director Brief"):
        DirectorRequest(brief, (evidence,), mismatched_script)
    with pytest.raises(ValueError, match="requires ScriptPlan"):
        DirectorRequest(brief, (evidence,), shooting_plan=mismatched_shooting)
    with pytest.raises(ValueError, match="exact Director ScriptPlan"):
        DirectorRequest(brief, (evidence,), valid_script, mismatched_shooting)


def test_workflow_without_eligible_analyzed_footage_fails_closed(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path)
    workspace.briefs.save(_brief())

    with pytest.raises(ValueError, match="eligible analyzed"):
        workspace.editing_runtime(director=FixedDirector()).editing.generate_edit_plan(
            GenerateEditPlanRequest("plan", EntityRevisionRef("brief", 1))
        )


def test_v6_codec_migration_and_immutable_conflict(tmp_path: Path) -> None:
    workspace = ProjectWorkspace.open(tmp_path)
    brief, _, _ = _seed(workspace)
    plan = workspace.editing_runtime(director=FixedDirector()).editing.generate_edit_plan(
        GenerateEditPlanRequest("plan", EntityRevisionRef(brief.envelope.id, 1))
    )
    assert decode_edit_plan(encode_edit_plan(plan)) == plan
    with workspace.database.write_connection() as connection:
        connection.execute("DROP TABLE edit_plans")
        connection.execute("PRAGMA user_version = 5")
    workspace.database.initialize()
    assert workspace.database.schema_version() == 6
    assert workspace.briefs.load(EntityRevisionRef("brief", 1)) == brief
    assert workspace.edit_plans.count() == 0
    with workspace.database.read_connection() as connection:
        migration = connection.execute(
            "SELECT from_version, to_version FROM project_migrations WHERE to_version = 6"
        ).fetchone()
    assert migration is not None and tuple(migration) == (5, 6)
    workspace.edit_plans.save(plan)
    changed = replace(plan, slots=(replace(plan.slots[0], purpose="different"),))
    with pytest.raises(RevisionConflictError):
        workspace.edit_plans.save(changed)


class FakeTransport:
    def __init__(self, content: dict[str, object]) -> None:
        self.content = content

    def create_chat_completion(self, payload: dict[str, object]) -> dict[str, object]:
        return {
            "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(self.content)}}]
        }


def test_deepseek_adapter_rejects_authority_bearing_extra_fields() -> None:
    port = DeepSeekDirectorPort(
        transport=FakeTransport(
            {
                "slots": [
                    {
                        "slot_id": "proof",
                        "order": 0,
                        "narrative_role": "proof",
                        "purpose": "show proof",
                        "semantic_query": "bottle pour",
                        "shot_id": "invented-shot",
                    }
                ]
            }
        ),
        config=DeepSeekChatConfig(),
    )
    request = DirectorRequest(
        _brief(),
        (
            DirectorFootageEvidence(
                EntityRevisionRef("shot", 1),
                EntityRevisionRef("asset", 1),
                1,
                AnalysisProfile.SEMANTIC,
                "summary",
                (),
                (),
                (),
            ),
        ),
    )
    with pytest.raises(DeepSeekPlanningResponseError, match="authority-bearing"):
        port.propose(request)


def test_director_proposal_contract_rejects_malformed_values() -> None:
    with pytest.raises(ValueError, match="both provided"):
        EditSlotProposal(
            "proof",
            0,
            "proof",
            "show proof",
            "bottle pour",
            minimum_duration=MediaTime(1, 1),
        )

    with pytest.raises(TypeError, match="allow_reuse"):
        EditSlotProposal(
            "proof",
            0,
            "proof",
            "show proof",
            "proof",
            allow_reuse="false",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field", "bad_value", "message"),
    (
        ("allow_reuse", "false", "allow_reuse must be a boolean"),
        ("order", 0.5, "order must be an integer"),
        ("purpose", 123, "purpose must be a string"),
        ("importance", 1.5, "importance must be an integer"),
    ),
)
def test_deepseek_adapter_rejects_malformed_scalar_types(
    field: str, bad_value: object, message: str
) -> None:
    slot: dict[str, object] = {
        "slot_id": "proof",
        "order": 0,
        "narrative_role": "proof",
        "purpose": "show proof",
        "semantic_query": "bottle pour",
    }
    slot[field] = bad_value
    port = DeepSeekDirectorPort(
        transport=FakeTransport({"slots": [slot]}),
        config=DeepSeekChatConfig(),
    )
    request = DirectorRequest(
        _brief(),
        (
            DirectorFootageEvidence(
                EntityRevisionRef("shot", 1),
                EntityRevisionRef("asset", 1),
                1,
                AnalysisProfile.SEMANTIC,
                "summary",
                (),
                (),
                (),
            ),
        ),
    )
    with pytest.raises(DeepSeekPlanningResponseError, match=message):
        port.propose(request)


def test_deepseek_adapter_rejects_non_integral_exact_time() -> None:
    port = DeepSeekDirectorPort(
        transport=FakeTransport(
            {
                "slots": [
                    {
                        "slot_id": "proof",
                        "order": 0,
                        "narrative_role": "proof",
                        "purpose": "show proof",
                        "semantic_query": "bottle pour",
                        "minimum_duration": {"value": 1.5, "scale": 1},
                        "maximum_duration": {"value": 2, "scale": 1},
                    }
                ]
            }
        ),
        config=DeepSeekChatConfig(),
    )
    request = DirectorRequest(
        _brief(),
        (
            DirectorFootageEvidence(
                EntityRevisionRef("shot", 1),
                EntityRevisionRef("asset", 1),
                1,
                AnalysisProfile.SEMANTIC,
                "summary",
                (),
                (),
                (),
            ),
        ),
    )
    with pytest.raises(DeepSeekPlanningResponseError, match="value/scale must be integers"):
        port.propose(request)
