from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

from video_editing_agent.adapters.cli.media_config import (
    transnetv2_detector,
    visual_understanding_port,
)
from video_editing_agent.adapters.cli.provider_config import (
    ProviderConfigurationError,
    deepseek_preproduction_ports,
)
from video_editing_agent.application.ports.preproduction_planning import PlanningPolicyGuidance
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.application.ports.shot_index import ShotCandidate
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetUsageRole
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.evidence.temporal import TemporalAnchor, TemporalEvidence
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.domain.shot.analysis import AnalysisProfile
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.media.understanding.frame_extraction import FfmpegPngFrameExtractor
from video_editing_agent.media.understanding.service import (
    ProviderNeutralVisualUnderstandingService,
)
from video_editing_agent.planning.brief.service import BriefContent
from video_editing_agent.planning.coverage.service import CoverageCandidate, CoverageReport
from video_editing_agent.planning.policy.builtin import (
    GENERIC_VERTICAL_SHORT_FORM_V1,
    NATURAL_VLOG_V1,
    PERFORMANCE_PRODUCT_AD_V1,
)
from video_editing_agent.planning.policy.guidance import to_planning_policy_guidance
from video_editing_agent.planning.policy.model import CommercialPolicySelection, MarketingObjective
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project import ProjectWorkspace
from video_editing_agent.storage.repositories.preproduction_codec import (
    decode_brief,
    encode_brief,
    encode_script_plan,
    encode_shooting_plan,
)
from video_editing_agent.storage.repositories.record_codec import (
    encode_asset,
    encode_shot,
    encode_shot_analysis,
)


def _entity_command(parent: argparse._SubParsersAction[Any], name: str) -> None:
    item = parent.add_parser(name)
    sub = item.add_subparsers(dest="action", required=True)
    show = sub.add_parser("show")
    show.add_argument("entity_id")
    show.add_argument("revision", type=int)


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
    revise = brief_sub.add_parser("revise")
    revise.add_argument("entity_id")
    revise.add_argument("revision", type=int)
    revise.add_argument("--json", type=Path, required=True)

    script = sub.add_parser("script")
    script_sub = script.add_subparsers(dest="action", required=True)
    script_show = script_sub.add_parser("show")
    script_show.add_argument("entity_id")
    script_show.add_argument("revision", type=int)
    for action in ("lock", "unlock"):
        lock = script_sub.add_parser(action)
        lock.add_argument("entity_id")
        lock.add_argument("revision", type=int)
        lock.add_argument("section_id")
    for action in ("generate", "revise"):
        command = script_sub.add_parser(action)
        command.add_argument("entity_id")
        command.add_argument("revision", type=int)
        command.add_argument("--provider", choices=("deepseek",), required=True)
        command.add_argument("--model", default="deepseek-v4-flash")
        command.add_argument("--policy-json", type=Path, required=True)
        if action == "revise":
            command.add_argument("--instruction", required=True)

    shooting = sub.add_parser("shooting")
    shooting_sub = shooting.add_subparsers(dest="action", required=True)
    shooting_show = shooting_sub.add_parser("show")
    shooting_show.add_argument("entity_id")
    shooting_show.add_argument("revision", type=int)
    shooting_generate = shooting_sub.add_parser("generate")
    shooting_generate.add_argument("entity_id")
    shooting_generate.add_argument("revision", type=int)
    shooting_generate.add_argument("--provider", choices=("deepseek",), required=True)
    shooting_generate.add_argument("--model", default="deepseek-v4-flash")
    shooting_generate.add_argument("--policy-json", type=Path, required=True)
    shooting_generate.add_argument("--constraints-json", type=Path, required=True)
    asset = sub.add_parser("asset")
    asset_sub = asset.add_subparsers(dest="action", required=True)
    asset_show = asset_sub.add_parser("show")
    asset_show.add_argument("entity_id")
    asset_show.add_argument("revision", type=int)
    asset_ingest = asset_sub.add_parser("ingest")
    asset_ingest.add_argument("--json", type=Path, required=True)
    shot = sub.add_parser("shot")
    shot_sub = shot.add_subparsers(dest="action", required=True)
    shot_show = shot_sub.add_parser("show")
    shot_show.add_argument("entity_id")
    shot_show.add_argument("revision", type=int)
    shot_detect = shot_sub.add_parser("detect")
    shot_detect.add_argument("asset_id")
    shot_detect.add_argument("asset_revision", type=int)
    shot_detect.add_argument("--detector", choices=("transnetv2",), required=True)
    shot_detect.add_argument("--model", type=Path, required=True)
    shot_detect.add_argument("--device", choices=("auto", "cpu", "cuda", "mps"), default="cpu")
    shot_detect.add_argument("--ffmpeg", default="ffmpeg")
    shot_detect.add_argument("--min-shot-duration-ms", type=int)
    shot_detect.add_argument("--max-shot-duration-ms", type=int)
    analysis = sub.add_parser("analysis")
    analysis_sub = analysis.add_subparsers(dest="action", required=True)
    analysis_show = analysis_sub.add_parser("show")
    analysis_show.add_argument("shot_id")
    analysis_show.add_argument("shot_revision", type=int)
    analysis_run = analysis_sub.add_parser("run")
    analysis_run.add_argument("shot_id")
    analysis_run.add_argument("shot_revision", type=int)
    analysis_run.add_argument("--provider", choices=("gemini", "openai"), required=True)
    analysis_run.add_argument("--model", required=True)
    analysis_run.add_argument("--ffmpeg", default="ffmpeg")
    analysis_run.add_argument(
        "--profile", choices=("semantic", "deep_visual", "editorial"), default="semantic"
    )

    index = sub.add_parser("index")
    index_sub = index.add_subparsers(dest="action", required=True)
    query = index_sub.add_parser("query")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=20)
    index_sub.add_parser("rebuild")

    coverage = sub.add_parser("coverage")
    coverage_sub = coverage.add_subparsers(dest="action", required=True)
    coverage_show = coverage_sub.add_parser("show")
    coverage_show.add_argument("shooting_id")
    coverage_show.add_argument("revision", type=int)

    for resource in ("evidence", "anchor"):
        item = sub.add_parser(resource)
        item_sub = item.add_subparsers(dest="action", required=True)
        command = item_sub.add_parser("list")
        command.add_argument("shot_id")
        command.add_argument("shot_revision", type=int)
    return parser


def _json(value: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(value))


def _candidate(value: ShotCandidate) -> dict[str, Any]:
    return {
        "shot_ref": {
            "entity_id": value.shot_ref.entity_id,
            "revision": value.shot_ref.revision,
        },
        "analysis_revision": value.analysis_revision,
        "retrieval_score": value.retrieval_score,
        "matched_terms": list(value.matched_terms),
    }


def _coverage_candidate(value: CoverageCandidate) -> dict[str, Any]:
    return {
        **_candidate(
            ShotCandidate(
                value.shot_ref,
                value.analysis_revision,
                value.retrieval_score,
                value.matched_terms,
            )
        ),
        "duration": {"value": value.duration.value, "scale": value.duration.scale},
    }


def _coverage(value: CoverageReport) -> dict[str, Any]:
    return {
        "shooting_plan_ref": {
            "entity_id": value.shooting_plan_ref.entity_id,
            "revision": value.shooting_plan_ref.revision,
        },
        "assessments": [
            {
                "requirement_id": item.requirement_id,
                "state": item.state.value,
                "action": item.action.value,
                "reason": item.reason,
                "reshoot_instruction": item.reshoot_instruction,
                "candidates": [_coverage_candidate(candidate) for candidate in item.candidates],
            }
            for item in value.assessments
        ],
    }


def _time(value: MediaTime) -> dict[str, int]:
    return {"value": value.value, "scale": value.scale}


def _temporal_evidence(value: TemporalEvidence) -> dict[str, Any]:
    return {
        "evidence_id": value.evidence_id,
        "shot_ref": {"entity_id": value.shot_ref.entity_id, "revision": value.shot_ref.revision},
        "kind": value.kind,
        "method": value.method,
        "producer_version": value.producer_version,
        "confidence": value.confidence,
        "source_range": None
        if value.source_range is None
        else {
            "start": _time(value.source_range.start),
            "duration": _time(value.source_range.duration),
        },
        "artifact_refs": list(value.artifact_refs),
        "source_refs": list(value.source_refs),
    }


def _temporal_anchor(value: TemporalAnchor) -> dict[str, Any]:
    return {
        "anchor_id": value.anchor_id,
        "shot_ref": {"entity_id": value.shot_ref.entity_id, "revision": value.shot_ref.revision},
        "kind": value.kind,
        "source_time": _time(value.source_time),
        "confidence": value.confidence,
        "evidence_refs": list(value.evidence_refs),
        "method": value.method,
        "semantic_label": value.semantic_label,
    }


def _policy(path: Path) -> PlanningPolicyGuidance:
    value = json.loads(path.read_text(encoding="utf-8"))
    skills = {
        PERFORMANCE_PRODUCT_AD_V1.skill_id: PERFORMANCE_PRODUCT_AD_V1,
        NATURAL_VLOG_V1.skill_id: NATURAL_VLOG_V1,
    }
    objective = value.get("marketing_objective")
    return to_planning_policy_guidance(
        CommercialPolicySelection(
            GENERIC_VERTICAL_SHORT_FORM_V1,
            skills[value["skill_id"]],
            None if objective is None else MarketingObjective(objective),
        )
    )


def _constraints(path: Path) -> ProductionConstraints:
    value = json.loads(path.read_text(encoding="utf-8"))
    return ProductionConstraints(
        camera_or_phone=value["camera_or_phone"],
        stabilizer=value.get("stabilizer"),
        lighting=value.get("lighting"),
        microphones=tuple(value.get("microphones", [])),
        people_count=value.get("people_count", 1),
        locations=tuple(ProductionLocation(**item) for item in value.get("locations", [])),
        available_time_notes=value.get("available_time_notes"),
        user_skill_level=value.get("user_skill_level"),
        notes=tuple(value.get("notes", [])),
    )


def _run(args: argparse.Namespace) -> object:
    workspace = ProjectWorkspace.open(args.project)
    if args.resource == "shot" and args.action == "detect":
        ref = EntityRevisionRef(args.asset_id, args.asset_revision)
        detector = transnetv2_detector(
            workspace.assets,
            model_path=args.model,
            device=args.device,
            ffmpeg_executable=args.ffmpeg,
        )
        shots = workspace.detect(
            ref,
            detector,
            ShotDetectionOptions(args.min_shot_duration_ms, args.max_shot_duration_ms),
        )
        return [_json(encode_shot(shot)) for shot in shots]
    if args.resource == "analysis" and args.action == "run":
        visual = visual_understanding_port(
            args.provider, model=args.model, artifacts=workspace.artifacts
        )
        service = ProviderNeutralVisualUnderstandingService(
            shot_repository=workspace.shots,
            asset_media_resolver=RepositoryLocalAssetMediaResolver(workspace.assets),
            analysis_repository=workspace.analyses,
            frame_extractor=FfmpegPngFrameExtractor(args.ffmpeg),
            artifact_store=workspace.artifacts,
            visual_port=visual,
        )
        analysis_result = service.analyze(
            EntityRevisionRef(args.shot_id, args.shot_revision), AnalysisProfile(args.profile)
        )
        return _json(encode_shot_analysis(analysis_result))
    if args.resource == "asset" and args.action == "ingest":
        value = json.loads(args.json.read_text(encoding="utf-8"))
        source = LocalMediaSource(
            Path(value["path"]),
            value["origin"],
            AssetProvenance(**value["provenance"]),
            None if value.get("usage_role") is None else AssetUsageRole(value["usage_role"]),
        )
        return _json(
            encode_asset(
                AssetIngestService(FfprobeMediaProbe(), repository=workspace.assets).ingest(
                    source, created_by="cli"
                )
            )
        )
    if args.resource == "script" and args.action in {"generate", "revise"}:
        ports = deepseek_preproduction_ports(model=args.model)
        runtime = workspace.runtime(
            script_planning=ports.script_planning,
            script_review=ports.script_review,
            shooting_planning=ports.shooting_planning,
            shooting_review=ports.shooting_review,
        )
        ref = EntityRevisionRef(args.entity_id, args.revision)
        script_result = (
            runtime.preproduction.generate_script(ref, _policy(args.policy_json))
            if args.action == "generate"
            else runtime.preproduction.revise_script(
                ref, args.instruction, _policy(args.policy_json)
            )
        )
        return _json(encode_script_plan(script_result))
    if args.resource == "shooting" and args.action == "generate":
        ports = deepseek_preproduction_ports(model=args.model)
        runtime = workspace.runtime(
            script_planning=ports.script_planning,
            script_review=ports.script_review,
            shooting_planning=ports.shooting_planning,
            shooting_review=ports.shooting_review,
        )
        return _json(
            encode_shooting_plan(
                runtime.preproduction.generate_shooting(
                    EntityRevisionRef(args.entity_id, args.revision),
                    _constraints(args.constraints_json),
                    _policy(args.policy_json),
                )
            )
        )
    if args.resource in {"project", "status"}:
        return workspace.status()
    if args.resource == "brief" and args.action == "create":
        return _json(
            encode_brief(
                workspace.brief_service.create(
                    BriefContent(
                        args.title, args.objective, args.audience, args.platform, args.core_message
                    ),
                    created_by="cli",
                )
            )
        )
    if args.resource == "brief" and args.action == "revise":
        content = BriefContent.from_brief(decode_brief(args.json.read_text(encoding="utf-8")))
        return _json(
            encode_brief(
                workspace.brief_service.revise(
                    EntityRevisionRef(args.entity_id, args.revision), content, created_by="cli"
                )
            )
        )
    if args.resource == "script" and args.action in {"lock", "unlock"}:
        locked_script = workspace.script_planner.set_section_lock(
            EntityRevisionRef(args.entity_id, args.revision),
            args.section_id,
            locked=args.action == "lock",
            created_by="cli",
        )
        return _json(encode_script_plan(locked_script))
    if args.resource == "analysis":
        analysis = workspace.analyses.latest(EntityRevisionRef(args.shot_id, args.shot_revision))
        if analysis is None:
            raise KeyError("Shot has no analysis")
        return _json(encode_shot_analysis(analysis))
    if args.resource == "index":
        if args.action == "rebuild":
            count = workspace.rebuild_index()
            return {
                "indexed_source_count": count,
                "sources": [
                    {
                        "shot_ref": {
                            "entity_id": item.shot.envelope.id,
                            "revision": item.shot.envelope.revision,
                        },
                        "analysis_revision": item.analysis.revision,
                    }
                    for item in workspace.index_sources()
                ],
            }
        return [
            _candidate(item) for item in workspace.shot_index.search(args.query, limit=args.limit)
        ]
    if args.resource == "coverage":
        plan = workspace.shooting_plans.load(EntityRevisionRef(args.shooting_id, args.revision))
        return _coverage(workspace.coverage.evaluate(plan))
    if args.resource in {"evidence", "anchor"}:
        ref = EntityRevisionRef(args.shot_id, args.shot_revision)
        values = (
            workspace.temporal.list_evidence(ref)
            if args.resource == "evidence"
            else workspace.temporal.list_anchors(ref)
        )
        return [
            _temporal_evidence(value)
            if isinstance(value, TemporalEvidence)
            else _temporal_anchor(value)
            for value in values
        ]

    ref = EntityRevisionRef(args.entity_id, args.revision)
    if args.resource == "brief":
        return _json(encode_brief(workspace.briefs.load(ref)))
    if args.resource == "script":
        return _json(encode_script_plan(workspace.scripts.load(ref)))
    if args.resource == "shooting":
        return _json(encode_shooting_plan(workspace.shooting_plans.load(ref)))
    if args.resource == "asset":
        return _json(encode_asset(workspace.assets.load(ref)))
    return _json(encode_shot(workspace.shots.load(ref)))


def main(argv: list[str] | None = None) -> int:
    try:
        result = _run(_parser().parse_args(argv))
    except (
        KeyError,
        TypeError,
        ValueError,
        OSError,
        RuntimeError,
        json.JSONDecodeError,
        ProviderConfigurationError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0
