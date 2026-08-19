from video_editing_agent.adapters.product.ui_theme import (
    DEFAULT_PRODUCT_THEME,
    DEFAULT_PRODUCT_TYPOGRAPHY,
    ProductThemeTokens,
    ProductTypography,
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
