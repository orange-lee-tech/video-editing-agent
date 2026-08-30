from pathlib import Path

import pytest

from video_editing_agent.system.windows_dpi import configure_tk_scaling


class _Tk:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def call(self, *args: object) -> None:
        self.calls.append(args)


class _Root:
    def __init__(self, dpi: float) -> None:
        self.dpi = dpi
        self.tk = _Tk()

    def winfo_fpixels(self, value: str) -> float:
        assert value == "1i"
        return self.dpi


def test_tk_scaling_uses_monitor_dpi() -> None:
    root = _Root(144.0)

    scale = configure_tk_scaling(root)

    assert scale == pytest.approx(2.0)
    assert root.tk.calls == [("tk", "scaling", pytest.approx(2.0))]


def test_desktop_entry_enables_dpi_before_product_ui_import() -> None:
    source = Path("src/video_editing_agent/adapters/bootstrap/desktop_entry.py").read_text(
        encoding="utf-8"
    )

    assert source.index("enable_windows_dpi_awareness()") < source.index(
        "from video_editing_agent.adapters.product.tkinter_app import launch"
    )
