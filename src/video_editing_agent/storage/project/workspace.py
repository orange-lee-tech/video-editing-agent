from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.application.ports.director import DirectorPort
from video_editing_agent.application.ports.preproduction_planning import (
    ScriptPlanningPort,
    ShootingPlanningPort,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReviewPort,
    ShootingProposalReviewPort,
)
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions, ShotDetector
from video_editing_agent.application.ports.shot_index import ShotIndexSource
from video_editing_agent.application.ports.understanding import UnderstandingService
from video_editing_agent.application.use_cases.editing_director import EditingDirectorWorkflow
from video_editing_agent.application.use_cases.runtime import (
    ApplicationRuntime,
    CoverageResult,
    EditingApplicationRuntime,
    EditingOperations,
    MediaOperations,
    PreproductionOperations,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.shot.model import Shot
from video_editing_agent.media.indexing.lexical import LexicalShotIndex
from video_editing_agent.media.ingest.probe import MediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.shot_detection.catalog import ShotCatalog
from video_editing_agent.planning.brief.service import BriefService
from video_editing_agent.planning.coverage.service import CoverageService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.script.workflow import ScriptPlanningWorkflow
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.planning.shooting.workflow import ShootingPlanningWorkflow
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.project.layout import WorkspaceWritableLayout
from video_editing_agent.storage.repositories.edl_repository import SqliteEDLRepository
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.speech_transcript_repository import (
    SqliteSpeechTranscriptRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
    SqliteEditPlanRepository,
    SqliteShotAnalysisRepository,
    SqliteShotRepository,
)
from video_editing_agent.storage.repositories.temporal_evidence_repository import (
    SqliteTemporalEvidenceRepository,
)


@dataclass(frozen=True, slots=True)
class ProjectWorkspace:
    """Infrastructure composition root for one deterministic local project directory."""

    root: Path
    database: SqliteProjectDatabase
    artifacts: LocalArtifactStore
    provider_audio: Path
    writable: WorkspaceWritableLayout
    briefs: SqliteBriefRepository
    scripts: SqliteScriptPlanRepository
    shooting_plans: SqliteShootingPlanRepository
    assets: SqliteAssetRepository
    shots: SqliteShotRepository
    analyses: SqliteShotAnalysisRepository
    edit_plans: SqliteEditPlanRepository
    edls: SqliteEDLRepository
    temporal: SqliteTemporalEvidenceRepository
    transcripts: SqliteSpeechTranscriptRepository
    shot_index: LexicalShotIndex
    coverage: CoverageService
    brief_service: BriefService
    script_planner: ScriptPlanner
    shooting_planner: ShootingPlanner

    @classmethod
    def open(cls, root: Path) -> ProjectWorkspace:
        resolved = root.expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        provider_audio = resolved / "provider_audio"
        provider_audio.mkdir(parents=True, exist_ok=True)
        writable = WorkspaceWritableLayout.ensure(resolved)
        database = SqliteProjectDatabase(resolved / "project.sqlite3")
        database.initialize()
        briefs = SqliteBriefRepository(database)
        scripts = SqliteScriptPlanRepository(database)
        shooting = SqliteShootingPlanRepository(database)
        assets = SqliteAssetRepository(database)
        shots = SqliteShotRepository(database)
        analyses = SqliteShotAnalysisRepository(database)
        edit_plans = SqliteEditPlanRepository(database)
        edls = SqliteEDLRepository(database)
        temporal = SqliteTemporalEvidenceRepository(database)
        transcripts = SqliteSpeechTranscriptRepository(database)
        shot_index = LexicalShotIndex()
        shot_by_ref = {
            EntityRevisionRef(shot.envelope.id, shot.envelope.revision): shot
            for shot in shots.list_all()
        }
        shot_index.rebuild(
            ShotIndexSource(shot=shot_by_ref[analysis.shot_ref], analysis=analysis)
            for analysis in analyses.list_latest()
            if analysis.shot_ref in shot_by_ref
        )
        return cls(
            root=resolved,
            database=database,
            artifacts=LocalArtifactStore(resolved / "artifacts"),
            provider_audio=provider_audio,
            writable=writable,
            briefs=briefs,
            scripts=scripts,
            shooting_plans=shooting,
            assets=assets,
            shots=shots,
            analyses=analyses,
            edit_plans=edit_plans,
            edls=edls,
            temporal=temporal,
            transcripts=transcripts,
            shot_index=shot_index,
            coverage=CoverageService(
                shot_index=shot_index, shot_repository=shots, asset_repository=assets
            ),
            brief_service=BriefService(briefs),
            script_planner=ScriptPlanner(brief_repository=briefs, script_plan_repository=scripts),
            shooting_planner=ShootingPlanner(
                script_plan_repository=scripts, shooting_plan_repository=shooting
            ),
        )

    def status(self) -> dict[str, object]:
        return {
            "workspace": str(self.root),
            "database": str(self.database.path),
            "schema_version": self.database.schema_version(),
            "artifacts": str(self.root / "artifacts"),
            "provider_audio": str(self.provider_audio),
            "writable": {
                "cache": str(self.writable.cache),
                "work": str(self.writable.work),
                "logs": str(self.writable.logs),
                "drafts": str(self.writable.drafts),
                "history": str(self.writable.history),
                "outputs": str(self.writable.outputs),
            },
            "counts": {
                "assets": len(self.assets.list_all()),
                "shots": len(self.shots.list_all()),
                "shot_analyses": len(self.analyses.list_latest()),
                "briefs": self.briefs.count(),
                "script_plans": self.scripts.count(),
                "shooting_plans": self.shooting_plans.count(),
                "edit_plans": self.edit_plans.count(),
                "edls": self.edls.count(),
            },
            "capabilities": {
                "local_persistence": True,
                "lexical_index": True,
                "coverage": True,
                "temporal_evidence_storage": True,
                "external_provider_configured": False,
            },
        }

    def index_sources(self) -> tuple[ShotIndexSource, ...]:
        shot_by_ref = {
            EntityRevisionRef(shot.envelope.id, shot.envelope.revision): shot
            for shot in self.shots.list_all()
        }
        return tuple(
            ShotIndexSource(shot=shot_by_ref[analysis.shot_ref], analysis=analysis)
            for analysis in self.analyses.list_latest()
            if analysis.shot_ref in shot_by_ref
        )

    def editing_runtime(self, *, director: DirectorPort) -> EditingApplicationRuntime:
        workflow = EditingDirectorWorkflow(
            briefs=self.briefs,
            scripts=self.scripts,
            shooting_plans=self.shooting_plans,
            assets=self.assets,
            shots=self.shots,
            analyses=self.analyses,
            edit_plans=self.edit_plans,
            director=director,
        )
        return EditingApplicationRuntime(EditingOperations(workflow.generate, self.edit_plans.load))

    def runtime(
        self,
        *,
        script_planning: ScriptPlanningPort,
        script_review: ScriptProposalReviewPort,
        shooting_planning: ShootingPlanningPort,
        shooting_review: ShootingProposalReviewPort,
        media_probe: MediaProbe | None = None,
        understanding: UnderstandingService | None = None,
    ) -> ApplicationRuntime:
        script_workflow = ScriptPlanningWorkflow(
            brief_repository=self.briefs,
            script_plan_repository=self.scripts,
            planning_port=script_planning,
            planner=self.script_planner,
            review_port=script_review,
        )
        shooting_workflow = ShootingPlanningWorkflow(
            brief_repository=self.briefs,
            script_plan_repository=self.scripts,
            shooting_plan_repository=self.shooting_plans,
            planning_port=shooting_planning,
            planner=self.shooting_planner,
            review_port=shooting_review,
        )
        return ApplicationRuntime(
            preproduction=PreproductionOperations(
                lambda ref, policy: script_workflow.generate(ref, policy_guidance=policy),
                lambda ref, instruction, policy: script_workflow.revise(
                    ref, instruction, policy_guidance=policy
                ),
                lambda ref, constraints, policy: shooting_workflow.generate(
                    ref, constraints, policy_guidance=policy
                ),
                lambda ref, policy, references: script_workflow.generate(
                    ref, policy_guidance=policy, reference_guidance=references
                ),
                lambda ref, constraints, policy, references: shooting_workflow.generate(
                    ref,
                    constraints,
                    policy_guidance=policy,
                    reference_guidance=references,
                ),
            ),
            media=None
            if media_probe is None or understanding is None
            else MediaOperations(
                lambda request: AssetIngestService(media_probe, repository=self.assets).ingest(
                    LocalMediaSource(
                        request.path, request.origin, request.provenance, request.usage_role
                    ),
                    created_by="application",
                ),
                lambda ref, detector, options: self._detect(ref, detector, options),
                understanding.analyze,
                self.rebuild_index,
                lambda query, limit: self.shot_index.search(query, limit=limit),
                lambda ref: self._coverage_result(ref),
            ),
        )

    def _detect(
        self, ref: EntityRevisionRef, detector: ShotDetector, options: ShotDetectionOptions
    ) -> tuple[Shot, ...]:
        self.assets.load(ref)
        return ShotCatalog(repository=self.shots).commit_boundaries(detector.detect(ref, options))

    def detect(
        self, ref: EntityRevisionRef, detector: ShotDetector, options: ShotDetectionOptions
    ) -> tuple[Shot, ...]:
        """Execute the existing detector-to-owner commit use case."""
        return self._detect(ref, detector, options)

    def rebuild_index(self) -> int:
        sources = self.index_sources()
        self.shot_index.rebuild(sources)
        return len(sources)

    def _coverage_result(self, ref: EntityRevisionRef) -> CoverageResult:
        report = self.coverage.evaluate(self.shooting_plans.load(ref))
        return CoverageResult(
            report.shooting_plan_ref,
            {
                "unresolved_required_ids": list(report.unresolved_required_ids),
                "assessments": [
                    {
                        "requirement_id": item.requirement_id,
                        "state": item.state.value,
                        "action": item.action.value,
                        "reason": item.reason,
                        "reshoot_instruction": item.reshoot_instruction,
                    }
                    for item in report.assessments
                ],
            },
        )
