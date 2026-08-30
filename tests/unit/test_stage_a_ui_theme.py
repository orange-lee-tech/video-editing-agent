from video_editing_agent.adapters.product.appearance_settings import AppearanceMode
from video_editing_agent.adapters.product.ui_theme import (
    DEFAULT_PRODUCT_THEME,
    DEFAULT_PRODUCT_TYPOGRAPHY,
    ProductThemeTokens,
    ProductTypography,
    theme_tokens,
)


def test_product_theme_tokens_are_stable_and_nonempty() -> None:
    tokens = DEFAULT_PRODUCT_THEME

    assert isinstance(tokens, ProductThemeTokens)
    assert tokens.app_background.startswith("#")
    assert tokens.surface.startswith("#")
    assert tokens.text_primary.startswith("#")
    assert tokens.accent.startswith("#")
    assert tokens.danger.startswith("#")
    assert tokens.space_xs < tokens.space_sm < tokens.space_md < tokens.space_xl


def test_product_typography_keeps_windows_system_fallbacks() -> None:
    typography = DEFAULT_PRODUCT_TYPOGRAPHY

    assert isinstance(typography, ProductTypography)
    assert typography.ui_family == "Segoe UI"
    assert typography.cjk_family == "Microsoft YaHei UI"
    assert typography.title_size > typography.section_size > typography.meta_size


def test_product_theme_modes_are_distinct_and_typography_is_legible() -> None:
    day = theme_tokens(AppearanceMode.DAY)
    comfort = theme_tokens(AppearanceMode.COMFORT)
    night = theme_tokens(AppearanceMode.NIGHT)

    assert len({day.app_background, comfort.app_background, night.app_background}) == 3
    assert night.text_primary != night.surface
    assert DEFAULT_PRODUCT_TYPOGRAPHY.body_size >= 11
    assert DEFAULT_PRODUCT_TYPOGRAPHY.meta_size >= 10
    assert DEFAULT_PRODUCT_TYPOGRAPHY.family_for_language("zh-CN") == "Microsoft YaHei UI"
    assert DEFAULT_PRODUCT_TYPOGRAPHY.family_for_language("en") == "Segoe UI"
