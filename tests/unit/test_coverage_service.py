from datetime import UTC, datetime

from video_editing_agent.application.ports.shot_index import ShotIndexSource
from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.shot.analysis import AnalysisProfile, ShotAnalysis, VisualSemantics
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.domain.shooting.model import CoveragePriority, ShootingPlan, ShotRequirement
from video_editing_agent.media.indexing.lexical import LexicalShotIndex
from video_editing_agent.planning.coverage.service import (
    CoverageAction,
    CoverageEvaluationPolicy,
    CoverageService,
    CoverageState,
)

NOW = datetime(2026, 8, 11, 19, 50, tzinfo=UTC)


class MemoryAssetRepository:
    def __init__(self, assets: tuple[Asset, ...]) -> None:
        self._assets = {
            EntityRevisionRef(asset.envelope.id, asset.envelope.revision): asset for asset in assets
        }

    def load(self, asset_ref: EntityRevisionRef) -> Asset:
        return self._assets[asset_ref]

    def save(self, asset: Asset) -> None:
        self._assets[EntityRevisionRef(asset.envelope.id, asset.envelope.revision)] = asset


class MemoryShotRepository:
    def __init__(self, shots: tuple[Shot, ...]) -> None:
        self._shots = {
            EntityRevisionRef(shot.envelope.id, shot.envelope.revision): shot for shot in shots
        }

    def load(self, shot_ref: EntityRevisionRef) -> Shot:
        return self._shots[shot_ref]


def envelope(entity_id: str) -> EntityEnvelope:
    return EntityEnvelope(
        id=entity_id,
        revision=1,
        schema_version="0.2",
        status=EntityStatus.VALID,
        created_at=NOW,
        created_by="test",
    )


def make_asset(asset_id: str, usage_role: AssetUsageRole) -> Asset:
    return Asset(
        envelope=envelope(asset_id),
        media_kind="video",
        origin="imported_local",
        usage_role=usage_role,
        storage_ref=f"file:///tmp/{asset_id}.mp4",
        content_hash="sha256:" + asset_id[-1] * 64,
        byte_size=100,
        provenance=AssetProvenance(origin_type="imported_local"),
        imported_at=NOW,
        duration=MediaTime(10, 1),
    )


def make_shot(shot_id: str, asset_id: str, duration: MediaTime) -> Shot:
    return Shot(
        envelope=envelope(shot_id),
        asset_ref=EntityRevisionRef(asset_id, 1),
        source_range=MediaTimeRange(start=MediaTime(0, 1), duration=duration),
        boundary_method="test",
    )


def make_analysis(shot_id: str, *tags: str) -> ShotAnalysis:
    return ShotAnalysis(
        shot_ref=EntityRevisionRef(shot_id, 1),
        revision=1,
        profile=AnalysisProfile.SEMANTIC,
        analyzed_at=NOW,
        visual=VisualSemantics(tags=tags),
    )


def make_plan(requirement: ShotRequirement) -> ShootingPlan:
    return ShootingPlan(
        envelope=envelope("shp_coverage"),
        script_plan_ref=EntityRevisionRef("scp_coverage", 1),
        requirements=(requirement,),
    )


def service_for(
    assets: tuple[Asset, ...],
    shots: tuple[Shot, ...],
    analyses: tuple[ShotAnalysis, ...],
    *,
    policy: CoverageEvaluationPolicy | None = None,
) -> CoverageService:
    shot_by_ref = {
        EntityRevisionRef(shot.envelope.id, shot.envelope.revision): shot for shot in shots
    }
    index = LexicalShotIndex()
    index.rebuild(
        ShotIndexSource(shot=shot_by_ref[analysis.shot_ref], analysis=analysis)
        for analysis in analyses
    )
    return CoverageService(
        shot_index=index,
        shot_repository=MemoryShotRepository(shots),
        asset_repository=MemoryAssetRepository(assets),
        policy=policy,
    )


def required_product_requirement() -> ShotRequirement:
    return ShotRequirement(
        requirement_id="req_product",
        script_section_ref="demo",
        purpose="Show product operation",
        subject="product",
        action="operate",
        target_duration=MediaTime(4, 1),
        minimum_duration=MediaTime(2, 1),
        priority=CoveragePriority.REQUIRED,
        capture_instruction="Film the product operating continuously for about four seconds.",
    )


def test_reference_only_visual_candidate_does_not_satisfy_coverage() -> None:
    asset = make_asset("ast_reference1", AssetUsageRole.REFERENCE_ANALYSIS_ONLY)
    shot = make_shot("sht_reference", asset.envelope.id, MediaTime(5, 1))
    analysis = make_analysis(shot.envelope.id, "product", "operate")

    assessment = service_for((asset,), (shot,), (analysis,)).evaluate(
        make_plan(required_product_requirement())
    ).assessments[0]

    assert assessment.state is CoverageState.UNMATCHED
    assert assessment.action is CoverageAction.RESHOOT_REQUIRED
    assert assessment.candidates == ()
    assert assessment.reshoot_instruction == (
        "Film the product operating continuously for about four seconds."
    )


def test_editable_local_candidate_meeting_target_satisfies_requirement() -> None:
    asset = make_asset("ast_editable1", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    shot = make_shot("sht_good", asset.envelope.id, MediaTime(5, 1))
    analysis = make_analysis(shot.envelope.id, "product", "operate")

    assessment = service_for((asset,), (shot,), (analysis,)).evaluate(
        make_plan(required_product_requirement())
    ).assessments[0]

    assert assessment.state is CoverageState.SATISFIED
    assert assessment.action is CoverageAction.NONE
    assert len(assessment.candidates) == 1
    assert assessment.reshoot_instruction is None


def test_matching_footage_below_declared_minimum_is_weak_and_requires_reshoot() -> None:
    asset = make_asset("ast_short1", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    shot = make_shot("sht_short", asset.envelope.id, MediaTime(1, 1))
    analysis = make_analysis(shot.envelope.id, "product", "operate")

    assessment = service_for((asset,), (shot,), (analysis,)).evaluate(
        make_plan(required_product_requirement())
    ).assessments[0]

    assert assessment.state is CoverageState.WEAK
    assert assessment.action is CoverageAction.RESHOOT_REQUIRED
    assert "minimum duration" in assessment.reason


def test_matching_footage_between_minimum_and_target_is_weak() -> None:
    asset = make_asset("ast_target1", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    shot = make_shot("sht_target", asset.envelope.id, MediaTime(3, 1))
    analysis = make_analysis(shot.envelope.id, "product", "operate")

    assessment = service_for((asset,), (shot,), (analysis,)).evaluate(
        make_plan(required_product_requirement())
    ).assessments[0]

    assert assessment.state is CoverageState.WEAK
    assert "target duration" in assessment.reason


def test_overcovered_state_requires_explicit_policy_threshold() -> None:
    first_asset = make_asset("ast_multi1", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    second_asset = make_asset("ast_multi2", AssetUsageRole.EDITABLE_VISUAL_FOOTAGE)
    first_shot = make_shot("sht_multi1", first_asset.envelope.id, MediaTime(5, 1))
    second_shot = make_shot("sht_multi2", second_asset.envelope.id, MediaTime(5, 1))
    analyses = (
        make_analysis(first_shot.envelope.id, "product", "operate"),
        make_analysis(second_shot.envelope.id, "product", "operate"),
    )
    plan = make_plan(required_product_requirement())

    default_assessment = service_for(
        (first_asset, second_asset),
        (first_shot, second_shot),
        analyses,
    ).evaluate(plan).assessments[0]
    configured_assessment = service_for(
        (first_asset, second_asset),
        (first_shot, second_shot),
        analyses,
        policy=CoverageEvaluationPolicy(overcovered_candidate_count=2),
    ).evaluate(plan).assessments[0]

    assert default_assessment.state is CoverageState.SATISFIED
    assert configured_assessment.state is CoverageState.OVERCOVERED


def test_recommended_gap_recommends_reshoot_but_optional_gap_does_not_require_it() -> None:
    recommended = ShotRequirement(
        "req_recommended",
        "detail",
        "Show detail",
        "detail",
        priority=CoveragePriority.RECOMMENDED,
    )
    optional = ShotRequirement(
        "req_optional",
        "detail",
        "Show detail",
        "detail",
        priority=CoveragePriority.OPTIONAL,
    )
    service = service_for((), (), ())

    recommended_assessment = service.evaluate(make_plan(recommended)).assessments[0]
    optional_assessment = service.evaluate(make_plan(optional)).assessments[0]

    assert recommended_assessment.action is CoverageAction.RESHOOT_RECOMMENDED
    assert optional_assessment.action is CoverageAction.NONE
