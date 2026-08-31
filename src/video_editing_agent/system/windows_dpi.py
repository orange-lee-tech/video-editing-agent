from __future__ import annotations

import ctypes
import os
from typing import Any

_PER_MONITOR_AWARE_V2 = -4
_PROCESS_PER_MONITOR_DPI_AWARE = 2


def enable_windows_dpi_awareness() -> str:
    """Enable the strongest available Windows DPI mode before Tk is created."""

    if os.name != "nt":
        return "not-windows"

    try:
        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return "unavailable"
        user32 = windll.user32
        setter = getattr(user32, "SetProcessDpiAwarenessContext", None)
        if setter is not None and setter(ctypes.c_void_p(_PER_MONITOR_AWARE_V2)):
            return "per-monitor-v2"
    except (AttributeError, OSError):
        pass

    try:
        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return "unavailable"
        shcore = windll.shcore
        setter = getattr(shcore, "SetProcessDpiAwareness", None)
        if setter is not None and setter(_PROCESS_PER_MONITOR_DPI_AWARE) in {0, 0x80070005}:
            return "per-monitor"
    except (AttributeError, OSError):
        pass

    try:
        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return "unavailable"
        user32 = windll.user32
        setter = getattr(user32, "SetProcessDPIAware", None)
        if setter is not None and setter():
            return "system"
    except (AttributeError, OSError):
        pass

    return "unavailable"


def configure_tk_scaling(root: Any) -> float:
    """Apply a bounded Tk point-to-pixel scale derived from the active monitor DPI."""

    try:
        dpi = float(root.winfo_fpixels("1i"))
    except (TypeError, ValueError):
        dpi = 96.0
    if not 48.0 <= dpi <= 384.0:
        dpi = 96.0
    scale = max(1.0, min(4.0, dpi / 72.0))
    root.tk.call("tk", "scaling", scale)
    return scale
