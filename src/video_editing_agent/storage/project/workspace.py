from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.application.ports.shot_index import ShotIndexSource
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.media.indexing.lexical import LexicalShotIndex
from video_editing_agent.planning.brief.service import BriefService
from video_editing_agent.planning.coverage.service import CoverageService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase
from video_editing_agent.storage.repositories.sqlite_repositories import (
    SqliteAssetRepository,
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
    briefs: SqliteBriefRepository
    scripts: SqliteScriptPlanRepository
    shooting_plans: SqliteShootingPlanRepository
    assets: SqliteAssetRepository
    shots: SqliteShotRepository
    analyses: SqliteShotAnalysisRepository
    temporal: SqliteTemporalEvidenceRepository
    shot_index: LexicalShotIndex
    coverage: CoverageService
    brief_service: BriefService
    script_planner: ScriptPlanner
    shooting_planner: ShootingPlanner

    @classmethod
    def open(cls, root: Path) -> ProjectWorkspace:
        resolved = root.expanduser().resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        database = SqliteProjectDatabase(resolved / "project.sqlite3")
        database.initialize()
        briefs = SqliteBriefRepository(database)
        scripts = SqliteScriptPlanRepository(database)
        shooting = SqliteShootingPlanRepository(database)
        assets = SqliteAssetRepository(database)
        shots = SqliteShotRepository(database)
        analyses = SqliteShotAnalysisRepository(database)
        temporal = SqliteTemporalEvidenceRepository(database)
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
            briefs=briefs,
            scripts=scripts,
            shooting_plans=shooting,
            assets=assets,
            shots=shots,
            analyses=analyses,
            temporal=temporal,
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
            "counts": {
                "assets": len(self.assets.list_all()),
                "shots": len(self.shots.list_all()),
                "shot_analyses": len(self.analyses.list_latest()),
                "briefs": self.briefs.count(),
                "script_plans": self.scripts.count(),
                "shooting_plans": self.shooting_plans.count(),
            },
            "capabilities": {
                "local_persistence": True,
                "lexical_index": True,
                "coverage": True,
                "temporal_evidence_storage": True,
                "external_provider_configured": False,
            },
        }
