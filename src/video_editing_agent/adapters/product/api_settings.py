from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass

SUPPORTED_VISUAL_PROVIDERS = ("gemini", "openai")


@dataclass(frozen=True, slots=True)
class ApiCapabilitySettings:
    """Session-local API capability settings for the ordinary product shell."""

    thinking_key: str = ""
    visual_key: str = ""
    visual_provider: str = "gemini"

    def __post_init__(self) -> None:
        normalized = self.visual_provider.strip().casefold()
        if normalized not in SUPPORTED_VISUAL_PROVIDERS:
            raise ValueError(
                "visual_provider must be one of: " + ", ".join(SUPPORTED_VISUAL_PROVIDERS)
            )
        object.__setattr__(self, "visual_provider", normalized)

    @property
    def is_complete(self) -> bool:
        return bool(self.thinking_key.strip() and self.visual_key.strip())


def settings_from_environment(
    environment: Mapping[str, str],
) -> ApiCapabilitySettings:
    thinking_key = environment.get("DEEPSEEK_API_KEY", "")
    gemini_key = environment.get("GEMINI_API_KEY", "")
    openai_key = environment.get("OPENAI_API_KEY", "")
    if gemini_key.strip():
        return ApiCapabilitySettings(thinking_key, gemini_key, "gemini")
    if openai_key.strip():
        return ApiCapabilitySettings(thinking_key, openai_key, "openai")
    return ApiCapabilitySettings(thinking_key, "", "gemini")


def apply_settings_to_environment(
    settings: ApiCapabilitySettings,
    environment: MutableMapping[str, str],
) -> None:
    """Apply capability settings to the existing provider environment contract."""

    thinking_key = settings.thinking_key.strip()
    visual_key = settings.visual_key.strip()

    if thinking_key:
        environment["DEEPSEEK_API_KEY"] = thinking_key
    else:
        environment.pop("DEEPSEEK_API_KEY", None)

    environment.pop("GEMINI_API_KEY", None)
    environment.pop("OPENAI_API_KEY", None)
    if visual_key:
        target = "GEMINI_API_KEY" if settings.visual_provider == "gemini" else "OPENAI_API_KEY"
        environment[target] = visual_key
