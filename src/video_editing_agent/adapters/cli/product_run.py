from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, cast

from video_editing_agent.adapters.cli.provider_config import (
    deepseek_director_port,
    deepseek_preproduction_ports,
)
from video_editing_agent.application.ports.shot_detector import ShotDetectionOptions
from video_editing_agent.application.use_cases.product_flow import (
    EditingProductRequest,
    EditingProductResult,
    PlanningProductRequest,
    PlanningProductResult,
    ProductBriefInput,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.domain.shooting.model import ProductionConstraints, ProductionLocation
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.understanding.frame_extraction import FfmpegPngFrameExtractor
from video_editing_agent.media.understanding.service import ProviderNeutralVisualUnderstandingService
from video_editing_agent.providers.review.ffmpeg_pcm import FFmpegPcmRenderedMediaQc
from video_editing_agent.render.edl_ffmpeg import FFmpegEDLRenderer
from video_editing_agent.storage.asset.repository_media import RepositoryLocalAssetMediaResolver
from video_editing_agent.storage.project.product_flow import (
    EditingProductCapabilities,
    PlanningProductCapabilities,
    build_editing_product_flow,
    build_planning_product_flow,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace

_SCHEMA_VERSION = 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video-editing-agent run")
    modes = parser.add_subparsers(dest="mode", required=True)

    planning = modes.add_parser("planning")
    planning.add_argument("--request", type=Path, required=True)
    planning.add_argument("--deepseek-model", default="deepseek-v4-flash")

    editing = modes.add_parser("editing")
    editing.add_argument("--request", type=Path, required=True)
    editing.add_argument("--deepseek-model", default="deepseek-v4-flash")
    editing.add_argument("--visual-provider", choices=("gemini", "openai"), required=True)
    editing.add_argument("--visual-model", required=True)
    editing.add_argument("--transnet-model", type=Path, required=True)
    editing.add_argument("--device", default="cpu")
    editing.add_argument("--ffmpeg", default="ffmpeg")
    editing.add_argument("--ffprobe", default="ffprobe")
    editing.add_argument("--output-width", type=int, default=1920)
    editing.add_argument("--output-height", type=int, default=1080)
    editing.add_argument("--output-fps", type=int, default=30)
    return parser


def _object(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return cast(dict[str, object], value)


def _strict_keys(
    value: dict[str, object],
    *,
    name: str,
    allowed: frozenset[str],
    required: frozenset[str],
) -> None:
    keys = frozenset(value)
    unknown = sorted(keys - allowed)
    missing = sorted(required - keys)
    if unknown:
        raise ValueError(f"{name} contains unsupported fields: {','.join(unknown)}")
    if missing:
        raise ValueError(f"{name} is missing required fields: {','.join(missing)}")


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _text(value, name)


def _string_tuple(value: object, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return tuple(_text(item, f"{name}[]") for item in value)


def _positive_time_seconds(value: object, name: str) -> MediaTime | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{name} must be a positive decimal seconds value")
    try:
        decimal = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a positive decimal seconds value") from exc
    if not decimal.is_finite() or decimal <= 0:
        raise ValueError(f"{name} must be > 0")
    exact = Fraction(decimal)
    return MediaTime(exact.numerator, exact.denominator)


def _path(base: Path, value: object, name: str) -> Path:
    raw = Path(_text(value, name)).expanduser()
    candidate = raw if raw.is_absolute() else base / raw
    return candidate.resolve(strict=False)


def _entity_ref(value: object, name: str) -> EntityRevisionRef | None:
    if value is None:
        return None
    data = _object(value, name)
    _strict_keys(
        data,
        name=name,
        allowed=frozenset({"entity_id", "revision"}),
        required=frozenset({"entity_id", "revision"}),
    )
    revision = data["revision"]
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError(f"{name}.revision must be an integer >= 1")
    return EntityRevisionRef(_text(data["entity_id"], f"{name}.entity_id"), revision)


def _brief(value: object) -> ProductBriefInput:
    data = _object(value, "brief")
    allowed = frozenset(
        {
            "title",
            "objective",
            "audience",
            "platform",
            "core_message",
            "product_topic",
            "target_duration_seconds",
            "style_emotion",
            "success_criteria",
            "prohibited_content",
            "brand_constraints",
            "user_notes",
        }
    )
    required = frozenset({"title", "objective", "audience", "platform", "core_message"})
    _strict_keys(data, name="brief", allowed=allowed, required=required)
    return ProductBriefInput(
        title=_text(data["title"], "brief.title"),
        objective=_text(data["objective"], "brief.objective"),
        audience=_text(data["audience"], "brief.audience"),
        platform=_text(data["platform"], "brief.platform"),
        core_message=_text(data["core_message"], "brief.core_message"),
        product_topic=_optional_text(data.get("product_topic"), "brief.product_topic"),
        target_duration=_positive_time_seconds(
            data.get("target_duration_seconds"), "brief.target_duration_seconds"
        ),
        style_emotion=_string_tuple(data.get("style_emotion"), "brief.style_emotion"),
        success_criteria=_string_tuple(
            data.get("success_criteria"), "brief.success_criteria"
        ),
        prohibited_content=_string_tuple(
            data.get("prohibited_content"), "brief.prohibited_content"
        ),
        brand_constraints=_string_tuple(
            data.get("brand_constraints"), "brief.brand_constraints"
        ),
        user_notes=_optional_text(data.get("user_notes"), "brief.user_notes"),
    )


def _production_constraints(value: object) -> ProductionConstraints:
    if value is None:
        return ProductionConstraints()
    data = _object(value, "production_constraints")
    allowed = frozenset(
        {
            "camera_or_phone",
            "stabilizer",
            "lighting",
            "microphones",
            "people_count",
            "locations",
            "available_time_notes",
            "user_skill_level",
            "notes",
        }
    )
    _strict_keys(data, name="production_constraints", allowed=allowed, required=frozenset())
    people_count = data.get("people_count")
    if people_count is not None and (
        isinstance(people_count, bool) or not isinstance(people_count, int)
    ):
        raise ValueError("production_constraints.people_count must be an integer or null")
    locations_value = data.get("locations", [])
    if not isinstance(locations_value, list):
        raise ValueError("production_constraints.locations must be a JSON array")
    locations: list[ProductionLocation] = []
    for index, raw_location in enumerate(locations_value):
        name = f"production_constraints.locations[{index}]"
        location = _object(raw_location, name)
        _strict_keys(
            location,
            name=name,
            allowed=frozenset({"location_id", "label", "notes"}),
            required=frozenset({"location_id", "label"}),
        )
        locations.append(
            ProductionLocation(
                _text(location["location_id"], f"{name}.location_id"),
                _text(location["label"], f"{name}.label"),
                _optional_text(location.get("notes"), f"{name}.notes"),
            )
        )
    return ProductionConstraints(
        camera_or_phone=_optional_text(
            data.get("camera_or_phone"), "production_constraints.camera_or_phone"
        ),
        stabilizer=_optional_text(data.get("stabilizer"), "production_constraints.stabilizer"),
        lighting=_optional_text(data.get("lighting"), "production_constraints.lighting"),
        microphones=_string_tuple(
            data.get("microphones"), "production_constraints.microphones"
        ),
        people_count=people_count,
        locations=tuple(locations),
        available_time_notes=_optional_text(
            data.get("available_time_notes"), "production_constraints.available_time_notes"
        ),
        user_skill_level=_optional_text(
            data.get("user_skill_level"), "production_constraints.user_skill_level"
        ),
        notes=_string_tuple(data.get("notes"), "production_constraints.notes"),
    )


def _load_payload(path: Path) -> tuple[dict[str, object], Path]:
    resolved = path.expanduser().resolve(strict=True)
    try:
        root = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"request file contains invalid JSON: {resolved}") from exc
    data = _object(root, "request")
    version = data.get("schema_version")
    if version != _SCHEMA_VERSION:
        raise ValueError(f"request.schema_version must be {_SCHEMA_VERSION}")
    return data, resolved.parent


def load_planning_request(path: Path) -> PlanningProductRequest:
    data, base = _load_payload(path)
    _strict_keys(
        data,
        name="planning request",
        allowed=frozenset({"schema_version", "project", "brief", "production_constraints"}),
        required=frozenset({"schema_version", "project", "brief"}),
    )
    return PlanningProductRequest(
        _path(base, data["project"], "project"),
        _brief(data["brief"]),
        _production_constraints(data.get("production_constraints")),
    )


def load_editing_request(path: Path) -> EditingProductRequest:
    data, base = _load_payload(path)
    _strict_keys(
        data,
        name="editing request",
        allowed=frozenset(
            {
                "schema_version",
                "project",
                "brief",
                "local_media",
                "output",
                "requires_audible_output",
                "script_plan_ref",
                "shooting_plan_ref",
            }
        ),
        required=frozenset({"schema_version", "project", "brief", "local_media", "output"}),
    )
    media_value = data["local_media"]
    if not isinstance(media_value, list) or not media_value:
        raise ValueError("local_media must be a non-empty JSON array")
    audible = data.get("requires_audible_output", True)
    if not isinstance(audible, bool):
        raise ValueError("requires_audible_output must be a boolean")
    return EditingProductRequest(
        _path(base, data["project"], "project"),
        _brief(data["brief"]),
        tuple(_path(base, item, "local_media[]") for item in media_value),
        _path(base, data["output"], "output"),
        audible,
        _entity_ref(data.get("script_plan_ref"), "script_plan_ref"),
        _entity_ref(data.get("shooting_plan_ref"), "shooting_plan_ref"),
    )


def _ref_json(value: EntityRevisionRef | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {"entity_id": value.entity_id, "revision": value.revision}


def _events_json(result: PlanningProductResult | EditingProductResult) -> list[dict[str, str]]:
    return [
        {"stage": event.stage.value, "message": event.message}
        for event in result.events
    ]


def planning_result_json(result: PlanningProductResult) -> dict[str, Any]:
    return {
        "schema_version": _SCHEMA_VERSION,
        "mode": "planning",
        "outcome": result.outcome.value,
        "project": str(result.project_location),
        "brief_ref": _ref_json(result.brief_ref),
        "script_plan_ref": _ref_json(result.script_plan_ref),
        "shooting_plan_ref": _ref_json(result.shooting_plan_ref),
        "events": _events_json(result),
        "diagnostic": result.diagnostic,
    }


def editing_result_json(result: EditingProductResult) -> dict[str, Any]:
    review = None
    if result.review_verdict is not None:
        verdict = result.review_verdict
        review = {
            "disposition": verdict.disposition.value,
            "correction_route": verdict.correction_route.value,
            "repair_attempt": verdict.repair_attempt,
            "findings": [
                {
                    "finding_id": finding.finding_id,
                    "severity": finding.severity.value,
                    "problem": finding.problem,
                    "recommended_action": finding.recommended_action,
                    "affected_owner": finding.affected_owner,
                }
                for finding in verdict.report.findings
            ],
        }
    return {
        "schema_version": _SCHEMA_VERSION,
        "mode": "editing",
        "outcome": result.outcome.value,
        "project": str(result.project_location),
        "brief_ref": _ref_json(result.brief_ref),
        "edit_plan_ref": _ref_json(result.edit_plan_ref),
        "edl_ref": _ref_json(result.edl_ref),
        "output": None if result.output_path is None else str(result.output_path),
        "review": review,
        "events": _events_json(result),
        "diagnostic": result.diagnostic,
    }


def _planning_main(args: argparse.Namespace) -> dict[str, Any]:
    request = load_planning_request(args.request)
    workspace = ProjectWorkspace.open(request.project_location)
    ports = deepseek_preproduction_ports(model=args.deepseek_model)
    flow = build_planning_product_flow(
        workspace,
        PlanningProductCapabilities(
            ports.script_planning,
            ports.script_review,
            ports.shooting_planning,
            ports.shooting_review,
        ),
    )
    return planning_result_json(flow.run(request))


def _editing_main(args: argparse.Namespace) -> dict[str, Any]:
    from video_editing_agent.adapters.cli.media_config import (
        transnetv2_detector,
        visual_understanding_port,
    )

    request = load_editing_request(args.request)
    workspace = ProjectWorkspace.open(request.project_location)
    visual = visual_understanding_port(
        args.visual_provider,
        model=args.visual_model,
        artifacts=workspace.artifacts,
    )
    local_media = RepositoryLocalAssetMediaResolver(workspace.assets)
    understanding = ProviderNeutralVisualUnderstandingService(
        shot_repository=workspace.shots,
        asset_media_resolver=local_media,
        analysis_repository=workspace.analyses,
        frame_extractor=FfmpegPngFrameExtractor(args.ffmpeg),
        artifact_store=workspace.artifacts,
        visual_port=visual,
    )
    detector = transnetv2_detector(
        workspace.assets,
        model_path=args.transnet_model,
        device=args.device,
        ffmpeg_executable=args.ffmpeg,
    )
    flow = build_editing_product_flow(
        workspace,
        EditingProductCapabilities(
            FfprobeMediaProbe(args.ffprobe),
            detector,
            ShotDetectionOptions(),
            understanding,
            deepseek_director_port(model=args.deepseek_model),
            FFmpegEDLRenderer(args.ffmpeg, args.ffprobe),
            FFmpegPcmRenderedMediaQc(args.ffmpeg, args.ffprobe),
            output_width=args.output_width,
            output_height=args.output_height,
            output_fps=args.output_fps,
        ),
    )
    return editing_result_json(flow.run(request))


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        payload = _planning_main(args) if args.mode == "planning" else _editing_main(args)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0
