from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from video_editing_agent.adapters.product.component_update import (
    apply_component_archives,
    plan_component_update,
    sha256_file,
)
from video_editing_agent.adapters.product.update_check import (
    DEFAULT_UPDATE_MANIFEST_URL,
    UpdateComponent,
    check_for_update,
)
from video_editing_agent.adapters.product.update_state import (
    default_update_state_path,
    load_update_state,
)

_SYNCHRONIZE = 0x00100000
_WAIT_OBJECT_0 = 0
_WAIT_TIMEOUT = 258


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Video Editing Agent component updater")
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--app-exe", type=Path, required=True)
    parser.add_argument("--current-version", required=True)
    parser.add_argument("--wait-pid", type=int, default=0)
    parser.add_argument("--manifest-url", default=DEFAULT_UPDATE_MANIFEST_URL)
    parser.add_argument("--language", choices=("zh-CN", "en"), default="zh-CN")
    return parser


def wait_for_process_exit(pid: int, *, timeout_ms: int = 30_000) -> None:
    if pid <= 0 or os.name != "nt":
        return
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return
    kernel32 = windll.kernel32
    handle = kernel32.OpenProcess(_SYNCHRONIZE, False, pid)
    if not handle:
        return
    try:
        result = kernel32.WaitForSingleObject(handle, timeout_ms)
        if result == _WAIT_TIMEOUT:
            raise TimeoutError("the running application did not exit before update timeout")
        if result != _WAIT_OBJECT_0:
            raise OSError(f"WaitForSingleObject failed with status {result}")
    finally:
        kernel32.CloseHandle(handle)


def download_component(
    component: UpdateComponent,
    destination: Path,
    *,
    progress: callable | None = None,
) -> None:
    request = Request(
        component.url,
        headers={"User-Agent": "VideoEditingAgent-Updater/1"},
    )
    received = 0
    with urlopen(request, timeout=30.0) as response:
        with destination.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                received += len(chunk)
                if progress is not None:
                    progress(received, component.size_bytes)
    if received != component.size_bytes:
        raise ValueError(
            f"downloaded size mismatch for {component.component_id}: "
            f"{received} != {component.size_bytes}"
        )
    if sha256_file(destination) != component.sha256:
        raise ValueError(f"downloaded SHA-256 mismatch for {component.component_id}")


def _text(language: str, key: str) -> str:
    catalog = {
        "zh-CN": {
            "title": "视频剪辑智能体更新",
            "checking": "正在检查补丁…",
            "downloading": "正在下载 {component}：{percent}%",
            "applying": "正在安装 {component}：{current}/{total}",
            "done": "更新完成，正在重新启动…",
            "failed": "更新失败，旧版本已恢复。\n\n{detail}",
            "full": "此版本需要完整安装包，无法使用当前补丁更新器。",
        },
        "en": {
            "title": "Video Editing Agent Update",
            "checking": "Checking patch update…",
            "downloading": "Downloading {component}: {percent}%",
            "applying": "Installing {component}: {current}/{total}",
            "done": "Update complete. Restarting…",
            "failed": "Update failed and the previous version was restored.\n\n{detail}",
            "full": "This release requires the full installer and cannot use this patch updater.",
        },
    }
    return catalog[language][key]


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(sys.argv[1:] if argv is None else argv)

    import tkinter as tk
    from tkinter import messagebox, ttk

    root = tk.Tk()
    root.title(_text(args.language, "title"))
    root.geometry("520x150")
    root.resizable(False, False)
    label = ttk.Label(root, text=_text(args.language, "checking"), wraplength=470)
    label.pack(fill="x", padx=24, pady=(24, 12))
    bar = ttk.Progressbar(root, mode="determinate", maximum=100, length=470)
    bar.pack(padx=24, pady=(0, 18))

    def ui(message: str, percent: int | None = None) -> None:
        def apply() -> None:
            label.configure(text=message)
            if percent is not None:
                bar.configure(value=max(0, min(100, percent)))
        root.after(0, apply)

    def worker() -> None:
        try:
            wait_for_process_exit(args.wait_pid)
            state_path = default_update_state_path(args.install_root)
            installed = load_update_state(state_path)
            result = check_for_update(
                current_version=args.current_version,
                manifest_url=args.manifest_url,
                timeout_seconds=8.0,
            )
            if result.error is not None or result.manifest is None:
                raise ValueError(result.error or "update manifest is unavailable")
            manifest = result.manifest
            plan = plan_component_update(installed, manifest)
            if plan.full_installer_required or not plan.patch_available:
                raise ValueError(_text(args.language, "full"))

            with tempfile.TemporaryDirectory(prefix="video-editing-agent-update-") as raw_temp:
                temp_root = Path(raw_temp)
                archives: list[tuple[UpdateComponent, Path]] = []
                for index, component in enumerate(plan.components):
                    archive = temp_root / f"{component.component_id}.zip"

                    def download_progress(received: int, total: int, *, item=component) -> None:
                        percent = 0 if total <= 0 else int((received * 100) / total)
                        ui(
                            _text(args.language, "downloading").format(
                                component=item.component_id,
                                percent=min(percent, 100),
                            ),
                            percent,
                        )

                    download_component(component, archive, progress=download_progress)
                    archives.append((component, archive))
                    ui(
                        _text(args.language, "downloading").format(
                            component=component.component_id,
                            percent=100,
                        ),
                        100,
                    )

                def apply_progress(component_id: str, current: int, total: int) -> None:
                    ui(
                        _text(args.language, "applying").format(
                            component=component_id,
                            current=current,
                            total=total,
                        ),
                        int((current * 100) / max(total, 1)),
                    )

                apply_component_archives(
                    install_root=args.install_root,
                    state_path=state_path,
                    target_application_version=manifest.version,
                    manifest=manifest,
                    archives=archives,
                    progress=apply_progress,
                )

            ui(_text(args.language, "done"), 100)
            subprocess.Popen([str(args.app_exe)], cwd=str(args.install_root))
            root.after(500, root.destroy)
        except Exception as exc:
            def fail() -> None:
                messagebox.showerror(
                    _text(args.language, "title"),
                    _text(args.language, "failed").format(
                        detail=f"{type(exc).__name__}: {exc}"
                    ),
                    parent=root,
                )
                root.destroy()
            root.after(0, fail)

    threading.Thread(target=worker, name="component-updater", daemon=True).start()
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
