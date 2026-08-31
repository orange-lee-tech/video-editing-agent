from pathlib import Path

from video_editing_agent.adapters.product.appearance_settings import (
    AppearanceMode,
    AppearancePreferences,
    load_appearance_preferences,
    save_appearance_preferences,
)


def test_appearance_preferences_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "appearance.json"

    save_appearance_preferences(path, AppearancePreferences(AppearanceMode.NIGHT))

    assert load_appearance_preferences(path).mode is AppearanceMode.NIGHT


def test_invalid_appearance_preferences_fail_open_to_day(tmp_path: Path) -> None:
    path = tmp_path / "appearance.json"
    path.write_text('{"mode":"unknown"}', encoding="utf-8")

    assert load_appearance_preferences(path).mode is AppearanceMode.DAY
