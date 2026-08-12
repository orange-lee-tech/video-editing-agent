from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from video_editing_agent.planning.brief.service import BriefService
from video_editing_agent.planning.script.service import ScriptPlanner
from video_editing_agent.planning.shooting.service import ShootingPlanner
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore
from video_editing_agent.storage.repositories.preproduction_repositories import (
    SqliteBriefRepository,
    SqliteScriptPlanRepository,
    SqliteShootingPlanRepository,
)
from video_editing_agent.storage.repositories.sqlite_database import SqliteProjectDatabase


@dataclass(frozen=True, slots=True)
class ProjectWorkspace:
    """Infrastructure composition root for one deterministic local project directory."""

    root: Path
    database: SqliteProjectDatabase
    artifacts: LocalArtifactStore
    briefs: SqliteBriefRepository
    scripts: SqliteScriptPlanRepository
    shooting_plans: SqliteShootingPlanRepository
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
        return cls(
            root=resolved,
            database=database,
            artifacts=LocalArtifactStore(resolved / "artifacts"),
            briefs=briefs,
            scripts=scripts,
            shooting_plans=shooting,
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
        }
