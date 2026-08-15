from __future__ import annotations

import argparse
import json
from pathlib import Path

from video_editing_agent.adapters.cli.provider_config import deepseek_director_port
from video_editing_agent.application.use_cases.editing_director import GenerateEditPlanRequest
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def main() -> int:
    parser = argparse.ArgumentParser(description="Live DeepSeek Director engineering probe")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--brief-id", required=True)
    parser.add_argument("--brief-revision", required=True, type=int)
    parser.add_argument("--edit-plan-id", required=True)
    args = parser.parse_args()
    workspace = ProjectWorkspace.open(args.project)
    plan = workspace.editing_runtime(director=deepseek_director_port()).editing.generate_edit_plan(
        GenerateEditPlanRequest(
            args.edit_plan_id,
            EntityRevisionRef(args.brief_id, args.brief_revision),
        )
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "edit_plan": {"id": plan.envelope.id, "revision": plan.envelope.revision},
                "brief_ref": {
                    "id": plan.brief_ref.entity_id if plan.brief_ref else None,
                    "revision": plan.brief_ref.revision if plan.brief_ref else None,
                },
                "slot_count": len(plan.slots),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
