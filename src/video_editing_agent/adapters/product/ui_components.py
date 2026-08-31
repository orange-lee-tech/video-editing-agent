from __future__ import annotations

from collections.abc import Callable
from typing import Any

from video_editing_agent.adapters.product.ui_theme import DEFAULT_PRODUCT_THEME, ProductThemeTokens


def create_brand_mark(
    parent: Any,
    *,
    size: int = 40,
    tokens: ProductThemeTokens = DEFAULT_PRODUCT_THEME,
) -> Any:
    """Create the dependency-free product mark used by the desktop shell."""

    import tkinter as tk

    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        highlightthickness=0,
        borderwidth=0,
        background=tokens.surface,
    )
    unit = max(size // 14, 2)
    offset_x = max((size - 12 * unit) // 2, 0)
    offset_y = max((size - 12 * unit) // 2, 0)
    blocks = (
        (2, 2, 10, 3),
        (2, 3, 3, 10),
        (9, 3, 10, 10),
        (2, 9, 10, 10),
        (4, 4, 5, 8),
        (5, 5, 6, 7),
        (6, 6, 7, 6),
        (11, 4, 12, 5),
        (10, 5, 11, 6),
        (11, 6, 12, 7),
        (10, 7, 11, 8),
    )
    for x1, y1, x2, y2 in blocks:
        canvas.create_rectangle(
            offset_x + x1 * unit,
            offset_y + y1 * unit,
            offset_x + x2 * unit,
            offset_y + y2 * unit,
            fill=tokens.text_primary,
            outline="",
            tags=("brand-ink",),
        )
    return canvas


def create_section_card(
    parent: Any,
    *,
    title: str,
    description: str | None = None,
) -> tuple[Any, Any]:
    """Return a semantic card and its content frame."""

    from tkinter import ttk

    card = ttk.LabelFrame(parent, text=title, style="Card.TLabelframe")
    card.columnconfigure(0, weight=1)
    row = 0
    if description:
        ttk.Label(
            card,
            text=description,
            style="Muted.TLabel",
            wraplength=720,
            justify="left",
        ).grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1
    body = ttk.Frame(card, style="Card.TFrame")
    body.grid(row=row, column=0, sticky="nsew")
    body.columnconfigure(1, weight=1)
    return card, body


def create_empty_state(parent: Any, *, title: str, description: str) -> Any:
    """Create a quiet result placeholder before a workflow has produced output."""

    from tkinter import ttk

    frame = ttk.Frame(parent, style="Subtle.TFrame", padding=20)
    frame.columnconfigure(0, weight=1)
    ttk.Label(frame, text=title, style="Section.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(
        frame,
        text=description,
        style="Muted.TLabel",
        wraplength=720,
        justify="left",
    ).grid(row=1, column=0, sticky="w", pady=(6, 0))
    return frame


def create_header_action(
    parent: Any,
    *,
    command: Callable[[], None],
    primary: bool = False,
) -> Any:
    """Create a header/action button with stable semantic hierarchy."""

    from tkinter import ttk

    return ttk.Button(
        parent,
        command=command,
        style="Primary.TButton" if primary else "Secondary.TButton",
    )


def recolor_brand_mark(canvas: Any, tokens: ProductThemeTokens) -> None:
    canvas.configure(background=tokens.surface)
    canvas.itemconfigure("brand-ink", fill=tokens.text_primary)
