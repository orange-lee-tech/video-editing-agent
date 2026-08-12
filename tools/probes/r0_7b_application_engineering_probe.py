from __future__ import annotations

import json
import tempfile
from pathlib import Path

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.storage.project import ProjectWorkspace


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="r0.7b-application-") as directory:
        root = Path(directory)
        workspace = ProjectWorkspace.open(root)
        brief = workspace.brief_service.create(
            BriefContent(
                "Engineering probe",
                "Verify offline application assembly.",
                "engineering",
                "local",
                "No provider call is required.",
            ),
            created_by="engineering-probe",
        )
        reopened = ProjectWorkspace.open(root)
        brief_ref = EntityRevisionRef(brief.envelope.id, brief.envelope.revision)
        assert reopened.briefs.load(brief_ref) == brief
        status = reopened.status()
        assert status["schema_version"] == 4
        assert status["counts"]["briefs"] == 1  # type: ignore[index]
        evidence = {
            "probe": "r0.7b-application-engineering",
            "classification": "engineering_complete",
            "workspace_schema": status["schema_version"],
            "workspace_reopen": True,
            "brief_revision_persistence": True,
            "offline_only": True,
            "external_provider_invoked": False,
            "visual_fallback": "reshoot_only",
            "capabilities": status["capabilities"],
        }
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
