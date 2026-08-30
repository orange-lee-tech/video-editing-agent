from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class AppearanceMode(StrEnum):
    DAY = "day"
    COMFORT = "comfort"
    NIGHT = "night"


@dataclass(frozen=True, slots=True)
class AppearancePreferences:
    mode: AppearanceMode = AppearanceMode.DAY


def load_appearance_preferences(path: Path) -> AppearancePreferences:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("appearance settings root must be an object")
        return AppearancePreferences(AppearanceMode(str(payload.get("mode", AppearanceMode.DAY))))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return AppearancePreferences()


def save_appearance_preferences(path: Path, preferences: AppearancePreferences) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            {"schema": "video-editing-agent-appearance/v1", "mode": preferences.mode.value},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)
