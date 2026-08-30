from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from video_editing_agent.adapters.product.appearance_settings import AppearanceMode


@dataclass(frozen=True, slots=True)
class ProductThemeTokens:
    app_background: str
    surface: str
    surface_subtle: str
    border: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_active: str
    success: str
    warning: str
    danger: str
    inverse_text: str
    radius_hint: int = 10
    space_xs: int = 4
    space_sm: int = 8
    space_md: int = 12
    space_lg: int = 16
    space_xl: int = 24


DAY_PRODUCT_THEME = ProductThemeTokens(
    app_background="#F7F8FA",
    surface="#FFFFFF",
    surface_subtle="#F1F3F6",
    border="#D9DEE7",
    text_primary="#17191F",
    text_secondary="#596273",
    accent="#4F46E5",
    accent_active="#4338CA",
    success="#137A51",
    warning="#9A5C00",
    danger="#B93333",
    inverse_text="#FFFFFF",
)

COMFORT_PRODUCT_THEME = ProductThemeTokens(
    app_background="#F3F1E8",
    surface="#FAF9F3",
    surface_subtle="#ECEADF",
    border="#D7D3C5",
    text_primary="#252722",
    text_secondary="#62675B",
    accent="#526A4D",
    accent_active="#40553C",
    success="#3D7351",
    warning="#906522",
    danger="#A7443E",
    inverse_text="#FFFFFF",
)

NIGHT_PRODUCT_THEME = ProductThemeTokens(
    app_background="#111318",
    surface="#191C22",
    surface_subtle="#232730",
    border="#343A46",
    text_primary="#E8EBF1",
    text_secondary="#AEB5C2",
    accent="#8B85FF",
    accent_active="#A8A3FF",
    success="#63C795",
    warning="#E2B864",
    danger="#F08080",
    inverse_text="#101217",
)

PRODUCT_THEMES = {
    AppearanceMode.DAY: DAY_PRODUCT_THEME,
    AppearanceMode.COMFORT: COMFORT_PRODUCT_THEME,
    AppearanceMode.NIGHT: NIGHT_PRODUCT_THEME,
}

DEFAULT_PRODUCT_THEME = DAY_PRODUCT_THEME


@dataclass(frozen=True, slots=True)
class ProductTypography:
    ui_family: str = "Segoe UI"
    cjk_family: str = "Microsoft YaHei UI"
    mono_family: str = "Cascadia Mono"
    title_size: int = 18
    section_size: int = 13
    body_size: int = 11
    meta_size: int = 10

    def family_for_language(self, language: str) -> str:
        return self.cjk_family if language == "zh-CN" else self.ui_family


DEFAULT_PRODUCT_TYPOGRAPHY = ProductTypography()


def theme_tokens(mode: AppearanceMode | str) -> ProductThemeTokens:
    try:
        normalized = mode if isinstance(mode, AppearanceMode) else AppearanceMode(mode)
    except ValueError:
        normalized = AppearanceMode.DAY
    return PRODUCT_THEMES[normalized]


def configure_product_theme(
    root: Any,
    *,
    mode: AppearanceMode | str = AppearanceMode.DAY,
    language: str = "zh-CN",
) -> ProductThemeTokens:
    """Configure semantic ttk styles and classic Tk defaults for the selected appearance."""

    from tkinter import ttk

    tokens = theme_tokens(mode)
    type_scale = DEFAULT_PRODUCT_TYPOGRAPHY
    family = type_scale.family_for_language(language)
    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    root.configure(background=tokens.app_background)
    root.option_add("*Font", (family, type_scale.body_size))
    root.option_add("*TCombobox*Listbox.font", (family, type_scale.body_size))
    root.option_add("*TCombobox*Listbox.background", tokens.surface)
    root.option_add("*TCombobox*Listbox.foreground", tokens.text_primary)
    root.option_add("*TCombobox*Listbox.selectBackground", tokens.accent)
    root.option_add("*TCombobox*Listbox.selectForeground", tokens.inverse_text)

    style.configure("TFrame", background=tokens.surface)
    style.configure(
        "TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size),
    )
    style.configure(
        "TLabelframe",
        background=tokens.surface,
        foreground=tokens.text_primary,
        bordercolor=tokens.border,
    )
    style.configure(
        "TLabelframe.Label",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size, "bold"),
    )
    style.configure(
        "TEntry",
        fieldbackground=tokens.surface,
        foreground=tokens.text_primary,
        insertcolor=tokens.text_primary,
        font=(family, type_scale.body_size),
    )
    style.configure(
        "TButton",
        background=tokens.surface_subtle,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size),
    )
    style.map("TButton", background=[("active", tokens.border)])
    style.configure(
        "TCheckbutton",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size),
    )
    style.configure(
        "TCombobox",
        fieldbackground=tokens.surface,
        background=tokens.surface,
        foreground=tokens.text_primary,
        arrowcolor=tokens.text_secondary,
        font=(family, type_scale.body_size),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", tokens.surface)],
        foreground=[("readonly", tokens.text_primary)],
        selectbackground=[("readonly", tokens.surface)],
        selectforeground=[("readonly", tokens.text_primary)],
    )

    style.configure("App.TFrame", background=tokens.app_background)
    style.configure("Header.TFrame", background=tokens.surface)
    style.configure("Card.TFrame", background=tokens.surface)
    style.configure("Subtle.TFrame", background=tokens.surface_subtle)
    style.configure("Nav.TFrame", background=tokens.app_background)

    style.configure(
        "AppTitle.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.title_size, "bold"),
    )
    style.configure(
        "Section.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.section_size, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size),
    )
    style.configure(
        "Muted.TLabel",
        background=tokens.surface,
        foreground=tokens.text_secondary,
        font=(family, type_scale.meta_size),
    )
    style.configure(
        "Status.TLabel",
        background=tokens.app_background,
        foreground=tokens.text_secondary,
        font=(family, type_scale.meta_size),
    )
    style.configure(
        "StatusPill.TLabel",
        background=tokens.surface_subtle,
        foreground=tokens.text_secondary,
        padding=(10, 5),
        font=(family, type_scale.meta_size, "bold"),
    )

    style.configure(
        "Primary.TButton",
        background=tokens.accent,
        foreground=tokens.inverse_text,
        borderwidth=0,
        padding=(18, 9),
        font=(family, type_scale.body_size, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", tokens.accent_active), ("disabled", tokens.border)],
        foreground=[("disabled", tokens.text_secondary)],
    )
    style.configure(
        "Secondary.TButton",
        background=tokens.surface_subtle,
        foreground=tokens.text_primary,
        borderwidth=0,
        padding=(11, 7),
        font=(family, type_scale.body_size),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", tokens.border), ("pressed", tokens.border)],
    )
    style.configure(
        "Ghost.TButton",
        background=tokens.surface,
        foreground=tokens.text_secondary,
        borderwidth=0,
        padding=(9, 6),
        font=(family, type_scale.body_size),
    )
    style.map(
        "Ghost.TButton",
        foreground=[("active", tokens.text_primary)],
        background=[("active", tokens.surface_subtle)],
    )
    style.configure(
        "Workflow.TButton",
        background=tokens.app_background,
        foreground=tokens.text_secondary,
        borderwidth=0,
        padding=(14, 8),
        font=(family, type_scale.body_size, "bold"),
    )
    style.configure(
        "WorkflowActive.TButton",
        background=tokens.surface,
        foreground=tokens.accent,
        borderwidth=0,
        padding=(14, 8),
        font=(family, type_scale.body_size, "bold"),
    )
    style.map(
        "Workflow.TButton",
        background=[("active", tokens.surface_subtle)],
        foreground=[("active", tokens.text_primary)],
    )
    style.map(
        "WorkflowActive.TButton",
        background=[("active", tokens.surface)],
    )
    style.configure(
        "Danger.TButton",
        background=tokens.surface,
        foreground=tokens.danger,
        bordercolor=tokens.border,
        padding=(12, 7),
        font=(family, type_scale.body_size),
    )

    style.configure(
        "Card.TLabelframe",
        background=tokens.surface,
        borderwidth=0,
        relief="flat",
        padding=tokens.space_lg,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.section_size, "bold"),
    )

    style.configure(
        "Product.TNotebook",
        background=tokens.app_background,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.layout("Product.TNotebook.Tab", [])
    style.configure(
        "Product.TNotebook.Tab",
        padding=(16, 9),
        background=tokens.surface_subtle,
        foreground=tokens.text_secondary,
        font=(family, type_scale.body_size, "bold"),
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
        insertcolor=tokens.text_primary,
        padding=7,
        font=(family, type_scale.body_size),
    )
    style.configure(
        "Product.TCombobox",
        fieldbackground=tokens.surface,
        background=tokens.surface,
        foreground=tokens.text_primary,
        arrowcolor=tokens.text_secondary,
        bordercolor=tokens.border,
        padding=6,
        font=(family, type_scale.body_size),
    )
    style.map(
        "Product.TCombobox",
        fieldbackground=[("readonly", tokens.surface)],
        foreground=[("readonly", tokens.text_primary)],
        selectbackground=[("readonly", tokens.surface)],
        selectforeground=[("readonly", tokens.text_primary)],
    )
    style.configure(
        "Product.TCheckbutton",
        background=tokens.surface,
        foreground=tokens.text_primary,
        font=(family, type_scale.body_size),
    )

    style.configure(
        "Primary.Horizontal.TProgressbar",
        troughcolor=tokens.surface_subtle,
        background=tokens.accent,
        bordercolor=tokens.surface_subtle,
        lightcolor=tokens.accent,
        darkcolor=tokens.accent,
    )
    return tokens
