from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ProductThemeTokens:
    app_background: str = "#F3F6FB"
    surface: str = "#FFFFFF"
    surface_subtle: str = "#EEF2F7"
    border: str = "#D9E1EC"
    text_primary: str = "#172033"
    text_secondary: str = "#667085"
    accent: str = "#2F6FED"
    accent_active: str = "#2459C3"
    success: str = "#138A5B"
    warning: str = "#B26A00"
    danger: str = "#C63D3D"
    radius_hint: int = 10
    space_xs: int = 4
    space_sm: int = 8
    space_md: int = 12
    space_lg: int = 16
    space_xl: int = 24


DEFAULT_PRODUCT_THEME = ProductThemeTokens()


@dataclass(frozen=True, slots=True)
class ProductTypography:
    ui_family: str = "Segoe UI"
    cjk_family: str = "Microsoft YaHei UI"
    mono_family: str = "Cascadia Mono"
    title_size: int = 18
    section_size: int = 12
    body_size: int = 10
    meta_size: int = 9


DEFAULT_PRODUCT_TYPOGRAPHY = ProductTypography()


def configure_product_theme(root: Any) -> None:
    """Configure semantic ttk styles without changing product behavior."""

    from tkinter import ttk

    tokens = DEFAULT_PRODUCT_THEME
    type_scale = DEFAULT_PRODUCT_TYPOGRAPHY
    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    root.configure(background=tokens.app_background)

    style.configure("App.TFrame", background=tokens.app_background)
    style.configure("Header.TFrame", background=tokens.surface)
    style.configure("Card.TFrame", background=tokens.surface)
    style.configure("Subtle.TFrame", background=tokens.surface_subtle)

    style.configure(
        "AppTitle.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(type_scale.ui_family, type_scale.title_size, "bold"),
    )
    style.configure(
        "Section.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(type_scale.ui_family, type_scale.section_size, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(type_scale.ui_family, type_scale.body_size),
    )
    style.configure(
        "Muted.TLabel",
        background=tokens.surface,
        foreground=tokens.text_secondary,
        font=(type_scale.ui_family, type_scale.meta_size),
    )
    style.configure(
        "Status.TLabel",
        background=tokens.app_background,
        foreground=tokens.text_secondary,
        font=(type_scale.ui_family, type_scale.meta_size),
    )

    style.configure(
        "Primary.TButton",
        background=tokens.accent,
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(18, 9),
        font=(type_scale.ui_family, type_scale.body_size, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", tokens.accent_active), ("disabled", tokens.border)],
        foreground=[("disabled", tokens.text_secondary)],
    )
    style.configure(
        "Secondary.TButton",
        background=tokens.surface,
        foreground=tokens.text_primary,
        bordercolor=tokens.border,
        lightcolor=tokens.border,
        darkcolor=tokens.border,
        padding=(12, 7),
        font=(type_scale.ui_family, type_scale.body_size),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", tokens.surface_subtle)],
    )
    style.configure(
        "Danger.TButton",
        background=tokens.surface,
        foreground=tokens.danger,
        bordercolor=tokens.border,
        padding=(12, 7),
        font=(type_scale.ui_family, type_scale.body_size),
    )

    style.configure(
        "Card.TLabelframe",
        background=tokens.surface,
        bordercolor=tokens.border,
        lightcolor=tokens.border,
        darkcolor=tokens.border,
        borderwidth=1,
        relief="solid",
        padding=tokens.space_lg,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(type_scale.ui_family, type_scale.section_size, "bold"),
    )

    style.configure(
        "Product.TNotebook",
        background=tokens.app_background,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "Product.TNotebook.Tab",
        padding=(16, 9),
        background=tokens.surface_subtle,
        foreground=tokens.text_secondary,
        font=(type_scale.ui_family, type_scale.body_size, "bold"),
    )
    style.map(
        "Product.TNotebook.Tab",
        background=[("selected", tokens.surface)],
        foreground=[("selected", tokens.accent)],
    )

    style.configure(
        "Product.TEntry",
        fieldbackground=tokens.surface,
        foreground=tokens.text_primary,
        bordercolor=tokens.border,
        lightcolor=tokens.border,
        darkcolor=tokens.border,
        padding=7,
    )
    style.configure(
        "Product.TCombobox",
        fieldbackground=tokens.surface,
        foreground=tokens.text_primary,
        bordercolor=tokens.border,
        padding=6,
    )

    style.configure(
        "Primary.Horizontal.TProgressbar",
        troughcolor=tokens.surface_subtle,
        background=tokens.accent,
        bordercolor=tokens.surface_subtle,
        lightcolor=tokens.accent,
        darkcolor=tokens.accent,
    )
