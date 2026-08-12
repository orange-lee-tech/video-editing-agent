from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.storage.project import ProjectWorkspace
from video_editing_agent.storage.repositories.preproduction_codec import (
    encode_brief,
    encode_script_plan,
    encode_shooting_plan,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video-editing-agent")
    parser.add_argument("--project", type=Path, required=True)
    sub = parser.add_subparsers(dest="resource", required=True)
    project = sub.add_parser("project")
    project_sub = project.add_subparsers(dest="action", required=True)
    project_sub.add_parser("init")
    project_sub.add_parser("status")
    status = sub.add_parser("status")
    status.set_defaults(action="show")
    brief = sub.add_parser("brief")
    brief_sub = brief.add_subparsers(dest="action", required=True)
    create = brief_sub.add_parser("create")
    for name in ("title", "objective", "audience", "platform", "core-message"):
        create.add_argument(f"--{name}", required=True)
    show = brief_sub.add_parser("show")
    show.add_argument("entity_id")
    show.add_argument("revision", type=int)
    for name in ("script", "shooting"):
        item = sub.add_parser(name)
        item_sub = item.add_subparsers(dest="action", required=True)
        command = item_sub.add_parser("show")
        command.add_argument("entity_id")
        command.add_argument("revision", type=int)
    return parser


def _run(args: argparse.Namespace) -> dict[str, Any]:
    workspace = ProjectWorkspace.open(args.project)
    if args.resource in {"project", "status"}:
        return workspace.status()
    if args.resource == "brief" and args.action == "create":
        brief = workspace.brief_service.create(
            BriefContent(
                title=args.title,
                objective=args.objective,
                audience=args.audience,
                platform=args.platform,
                core_message=args.core_message,
            ),
            created_by="cli",
        )
        return cast(dict[str, Any], json.loads(encode_brief(brief)))
    ref = EntityRevisionRef(args.entity_id, args.revision)
    if args.resource == "brief":
        return cast(dict[str, Any], json.loads(encode_brief(workspace.briefs.load(ref))))
    if args.resource == "script":
        return cast(dict[str, Any], json.loads(encode_script_plan(workspace.scripts.load(ref))))
    return cast(
        dict[str, Any],
        json.loads(encode_shooting_plan(workspace.shooting_plans.load(ref))),
    )


def main(argv: list[str] | None = None) -> int:
    try:
        result = _run(_parser().parse_args(argv))
    except (KeyError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0
