from __future__ import annotations

import json
from pathlib import Path

import pytest

from video_editing_agent.adapters.cli.product_run import (
    load_editing_request,
    load_planning_request,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime


def _write(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _brief() -> dict[str, object]:
    return {
        "title": "Product value",
        "objective": "Show the product clearly",
        "audience": "buyers",
        "platform": "short-video",
        "core_message": "The product is useful",
        "target_duration_seconds": "12.5",
        "style_emotion": ["clear", "confident"],
    }


def test_planning_request_parses_product_fields_and_relative_project(tmp_path: Path) -> None:
    request_path = _write(
        tmp_path / "planning.json",
        {
            "schema_version": 1,
            "project": "project",
            "brief": _brief(),
            "production_constraints": {
                "camera_or_phone": "phone",
                "people_count": 1,
                "locations": [{"location_id": "desk", "label": "Desk"}],
            },
        },
    )

    request = load_planning_request(request_path)

    assert request.project_location == (tmp_path / "project").resolve()
    assert request.brief.target_duration == MediaTime(25, 2)
    assert request.production_constraints.camera_or_phone == "phone"
    assert request.production_constraints.people_count == 1
    assert request.production_constraints.locations[0].location_id == "desk"


def test_editing_request_parses_only_product_inputs_and_optional_planning_refs(
    tmp_path: Path,
) -> None:
    request_path = _write(
        tmp_path / "editing.json",
        {
            "schema_version": 1,
            "project": "project",
            "brief": _brief(),
            "local_media": ["media/a.mp4", "media/b.mp4"],
            "output": "output/final.mp4",
            "requires_audible_output": False,
            "script_plan_ref": {"entity_id": "scp_1", "revision": 2},
            "shooting_plan_ref": {"entity_id": "shp_1", "revision": 3},
        },
    )

    request = load_editing_request(request_path)

    assert request.project_location == (tmp_path / "project").resolve()
    assert request.local_media_paths == (
        (tmp_path / "media/a.mp4").resolve(),
        (tmp_path / "media/b.mp4").resolve(),
    )
    assert request.output_path == (tmp_path / "output/final.mp4").resolve()
    assert request.requires_audible_output is False
    assert request.script_plan_ref == EntityRevisionRef("scp_1", 2)
    assert request.shooting_plan_ref == EntityRevisionRef("shp_1", 3)


@pytest.mark.parametrize(
    "forbidden_field",
    (
        "shot_ref",
        "candidate_window",
        "resolution_decision",
        "source_timestamp",
        "audio_mix",
        "edl",
        "visual_provider",
        "transnet_model",
    ),
)
def test_editing_request_rejects_internal_or_runtime_fields(
    tmp_path: Path,
    forbidden_field: str,
) -> None:
    payload: dict[str, object] = {
        "schema_version": 1,
        "project": "project",
        "brief": _brief(),
        "local_media": ["media/a.mp4"],
        "output": "output/final.mp4",
        forbidden_field: "forbidden",
    }
    request_path = _write(tmp_path / f"editing-{forbidden_field}.json", payload)

    with pytest.raises(ValueError, match="unsupported fields"):
        load_editing_request(request_path)


def test_shooting_plan_ref_without_script_plan_ref_fails_closed(tmp_path: Path) -> None:
    request_path = _write(
        tmp_path / "editing-invalid-ref.json",
        {
            "schema_version": 1,
            "project": "project",
            "brief": _brief(),
            "local_media": ["media/a.mp4"],
            "output": "output/final.mp4",
            "shooting_plan_ref": {"entity_id": "shp_1", "revision": 1},
        },
    )

    with pytest.raises(ValueError, match="shooting_plan_ref requires script_plan_ref"):
        load_editing_request(request_path)
