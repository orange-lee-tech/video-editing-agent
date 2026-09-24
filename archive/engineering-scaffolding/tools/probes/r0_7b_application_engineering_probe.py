from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, cast

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanProposal,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReview,
    ScriptProposalViolation,
    ShootingProposalReview,
    ShootingProposalViolation,
)
from video_editing_agent.application.ports.shot_detector import (
    ShotBoundaryProposal,
    ShotDetectionOptions,
)
from video_editing_agent.application.ports.visual_understanding import (
    VisualSemanticsProposal,
    VisualUnderstandingRequest,
)
from video_editing_agent.application.use_cases.runtime import AssetIngestRequest
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.media.ingest.probe import MediaTechnicalMetadata
from video_editing_agent.media.understanding.frame_extraction import (
    PNG_MEDIA_TYPE,
    PNG_SIGNATURE,
    ExtractedFrameSample,
)
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
)
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.planning.coverage.service import CoverageAction, CoverageState
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project import ProjectWorkspace


class DeterministicProbe:
    calls = 0

    def probe(self, path: Path) -> MediaTechnicalMetadata:
        self.calls += 1
        if not path.is_file():
            raise FileNotFoundError(path)
        return MediaTechnicalMetadata("video", duration_ms=2_000, width=16, height=9)


class DeterministicDetector:
    calls = 0

    def detect(self, asset_ref: EntityRevisionRef, options: ShotDetectionOptions):
        self.calls += 1
        del options
        return (
            ShotBoundaryProposal(asset_ref, 0, 1_000, "probe-fake"),
            ShotBoundaryProposal(asset_ref, 1_000, 2_000, "probe-fake"),
        )


class ScriptedPort:
    def __init__(self, *values: object) -> None:
        self.values = values
        self.calls = 0

    def propose(self, request: object) -> object:
        del request
        value = self.values[self.calls]
        self.calls += 1
        return value


class ScriptedReviewer:
    def __init__(self, *values: object) -> None:
        self.values = values
        self.calls = 0

    def review(self, request: object) -> object:
        del request
        value = self.values[self.calls]
        self.calls += 1
        return value


class FakeFrameExtractor:
    calls = 0

    def extract(self, input_video: Path, plan: Any):
        self.calls += 1
        assert input_video.is_file()
        return tuple(
            ExtractedFrameSample(sample, PNG_MEDIA_TYPE, PNG_SIGNATURE + bytes([sample.ordinal]))
            for sample in plan.samples
        )


class ObservedVisualProvider:
    calls = 0

    def analyze(self, request: VisualUnderstandingRequest) -> VisualSemanticsProposal:
        self.calls += 1
        assert request.frames
        return VisualSemanticsProposal(
            summary="Product operates in entryway",
            tags=("product", "operate", "entryway"),
            subjects=("product",),
            actions=("operate",),
            environment="entryway",
        )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="r0_7b_engineering_") as directory:
        root = Path(directory)
        fixture = root / "fixture.mp4"
        fixture.write_bytes(b"deterministic local fixture")
        workspace = ProjectWorkspace.open(root / "project")
        probe = DeterministicProbe()
        detector = DeterministicDetector()
        visual = ObservedVisualProvider()
        extractor = FakeFrameExtractor()
        understanding = ProviderNeutralVisualUnderstandingService(
            shot_repository=workspace.shots,
            asset_media_resolver=RepositoryLocalAssetMediaResolver(workspace.assets),
            analysis_repository=workspace.analyses,
            frame_extractor=extractor,
            artifact_store=workspace.artifacts,
            visual_port=visual,
        )
        unsafe_script = ScriptPlanProposal(
            (
                NarrativeSectionProposal(
                    "demo", "proof", "Show product", spoken_content="Unsupported"
                ),
            )
        )
        safe_script = ScriptPlanProposal(
            (NarrativeSectionProposal("demo", "proof", "Show product", spoken_content="Observed"),)
        )
        script_port = ScriptedPort(unsafe_script, safe_script)
        script_review = ScriptedReviewer(
            ScriptProposalReview(
                False, (ScriptProposalViolation("unsupported_claim", "Remove unsupported claim"),)
            ),
            ScriptProposalReview(True),
        )
        unsafe_shooting = ShootingPlanProposal(
            (ShotRequirementProposal("req_match", "demo", "Show operation", "product"),)
        )
        safe_shooting = ShootingPlanProposal(
            (
                ShotRequirementProposal(
                    "req_match", "demo", "Show operation", "product", action="operate"
                ),
                ShotRequirementProposal(
                    "req_missing",
                    "demo",
                    "Show packaging",
                    "packaging",
                    priority="required",
                    capture_instruction="Film the packaging clearly.",
                ),
            )
        )
        shooting_port = ScriptedPort(unsafe_shooting, safe_shooting)
        shooting_review = ScriptedReviewer(
            ShootingProposalReview(
                False, (ShootingProposalViolation("missing_action", "Add exact action"),)
            ),
            ShootingProposalReview(True),
        )
        runtime = workspace.runtime(
            script_planning=cast(Any, script_port),
            script_review=cast(Any, script_review),
            shooting_planning=cast(Any, shooting_port),
            shooting_review=cast(Any, shooting_review),
            media_probe=probe,
            understanding=understanding,
        )
        assert runtime.media is not None
        asset = runtime.media.ingest(
            AssetIngestRequest(fixture, "captured", AssetProvenance("captured"))
        )
        asset_ref = EntityRevisionRef(asset.envelope.id, 1)
        shots = runtime.media.detect(asset_ref, detector, ShotDetectionOptions())
        assert tuple(shot.source_start_ms for shot in shots) == (0, 1_000)
        assert tuple(shot.source_end_ms for shot in shots) == (1_000, 2_000)
        first_shot_ref = EntityRevisionRef(shots[0].envelope.id, 1)
        analysis = runtime.media.analyze(first_shot_ref, AnalysisProfile.SEMANTIC)
        assert analysis.revision == 1 and visual.calls == extractor.calls == 1
        assert runtime.media.rebuild_index() == 1
        candidates = runtime.media.query_index("product operate", 5)
        assert candidates[0].shot_ref == first_shot_ref
        assert candidates[0].analysis_revision == 1

        brief = workspace.brief_service.create(
            BriefContent("Product demo", "Factual demo", "viewer", "vertical", "Show operation")
        )
        script = runtime.preproduction.generate_script(
            EntityRevisionRef(brief.envelope.id, 1), None
        )
        assert script_port.calls == script_review.calls == 2
        locked = workspace.script_planner.set_section_lock(
            EntityRevisionRef(script.envelope.id, 1), "demo", locked=True
        )
        revision_port = ScriptedPort(
            ScriptPlanProposal(
                (
                    NarrativeSectionProposal(
                        "demo",
                        "proof",
                        "Show product",
                        spoken_content=locked.sections[0].spoken_content,
                        locked=True,
                    ),
                )
            )
        )
        revision_runtime = workspace.runtime(
            script_planning=cast(Any, revision_port),
            script_review=cast(Any, ScriptedReviewer(ScriptProposalReview(True))),
            shooting_planning=cast(Any, shooting_port),
            shooting_review=cast(Any, shooting_review),
        )
        revised = revision_runtime.preproduction.revise_script(
            EntityRevisionRef(locked.envelope.id, 2), "Preserve locked section", None
        )
        assert revised.locked_section_ids == ("demo",)
        constraints = ProductionConstraints(
            "phone",
            locations=(ProductionLocation("loc_entry", "entryway"),),
            people_count=1,
        )
        plan = revision_runtime.preproduction.generate_shooting(
            EntityRevisionRef(revised.envelope.id, revised.envelope.revision), constraints, None
        )
        assert shooting_port.calls == shooting_review.calls == 2
        report = workspace.coverage.evaluate(plan)
        states = {item.requirement_id: item.state for item in report.assessments}
        actions = {item.requirement_id: item.action for item in report.assessments}
        assert states["req_match"] is CoverageState.SATISFIED
        assert actions["req_missing"] is CoverageAction.RESHOOT_REQUIRED

        evidence_item = TemporalEvidence(
            "ev_probe",
            first_shot_ref,
            "visual_cut",
            "probe-method",
            "1.0",
            0.9,
            MediaTimeRange(MediaTime(1, 3), MediaTime(1, 3)),
            analysis.artifact_refs,
        )
        anchor = TemporalAnchor(
            "anc_probe",
            first_shot_ref,
            "action",
            MediaTime(1, 2),
            0.8,
            (evidence_item.evidence_id,),
            "probe-anchor",
            "operate",
        )
        workspace.temporal.save_evidence(evidence_item)
        workspace.temporal.save_anchor(anchor)
        reopened = ProjectWorkspace.open(root / "project")
        assert reopened.assets.load(asset_ref) == asset
        persisted_shots = tuple(
            sorted(reopened.shots.list_all(), key=lambda shot: shot.source_start_ms)
        )
        assert tuple(
            (shot.envelope.id, shot.envelope.revision, shot.source_range)
            for shot in persisted_shots
        ) == tuple((shot.envelope.id, shot.envelope.revision, shot.source_range) for shot in shots)
        assert probe.calls == detector.calls == 1
        assert reopened.analyses.latest(first_shot_ref) == analysis
        assert reopened.scripts.load(
            EntityRevisionRef(revised.envelope.id, 3)
        ).locked_section_ids == ("demo",)
        assert (
            reopened.shooting_plans.load(EntityRevisionRef(plan.envelope.id, 1)).constraints
            == constraints
        )
        assert reopened.temporal.list_evidence(first_shot_ref) == (evidence_item,)
        assert reopened.temporal.list_anchors(first_shot_ref) == (anchor,)
        reopened_report = reopened.coverage.evaluate(
            reopened.shooting_plans.load(EntityRevisionRef(plan.envelope.id, 1))
        )
        assert reopened_report.assessments == report.assessments
        evidence = {
            "probe": "r0.7b-application-engineering",
            "classification": "engineering_complete",
            "asset_ingest_observed": True,
            "shot_detection_observed": True,
            "cross_process_persistence_observed": True,
            "media_probe_calls": probe.calls,
            "shot_detector_calls": detector.calls,
            "external_provider_invoked": False,
            "visual_provider_calls": visual.calls,
            "script_planning_calls": script_port.calls + revision_port.calls,
            "script_review_calls": script_review.calls + 1,
            "shooting_planning_calls": shooting_port.calls,
            "shooting_review_calls": shooting_review.calls,
            "index_result": {
                "shot_ref": first_shot_ref.entity_id,
                "analysis_revision": candidates[0].analysis_revision,
            },
            "coverage_states": {key: value.value for key, value in states.items()},
            "coverage_actions": {key: value.value for key, value in actions.items()},
            "temporal_method": evidence_item.method,
            "temporal_version": evidence_item.producer_version,
            "persisted_counts": reopened.status()["counts"],
        }
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
