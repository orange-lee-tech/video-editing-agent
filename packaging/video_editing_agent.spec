from pathlib import Path

repo = Path(SPECPATH).parent
payloads = repo / "build/runtime-payloads"

a = Analysis(
    [str(repo / "src/video_editing_agent/adapters/bootstrap/desktop_entry.py")],
    pathex=[str(repo / "src")],
    binaries=[],
    datas=[
        (
            str(repo / "resources/packaging/runtime-manifest.json"),
            "resources/packaging",
        ),
        (
            str(repo / "resources/packaging/runtime-manifest.schema.json"),
            "resources/packaging",
        ),
        (str(repo / "resources/licenses/THIRD_PARTY_RUNTIME_NOTICES.md"), "licenses"),
        (str(payloads / "ffmpeg-owned"), "tools"),
        (str(payloads / "python-stdlib"), "runtimes/python-stdlib"),
        (str(payloads / "transnet"), "runtimes/transnet"),
    ],
    hiddenimports=["tkinter", "tkinter.ttk"],
    excludes=["faster_whisper", "ctranslate2", "av", "transnetv2_pytorch", "torch", "mediapipe"],
    noarchive=False,
)
updater_a = Analysis(
    [str(repo / "src/video_editing_agent/adapters/bootstrap/updater_entry.py")],
    pathex=[str(repo / "src")],
    binaries=[],
    datas=[],
    hiddenimports=["tkinter", "tkinter.ttk"],
    excludes=["faster_whisper", "ctranslate2", "av", "transnetv2_pytorch", "torch", "mediapipe"],
    noarchive=False,
)
updater_pyz = PYZ(updater_a.pure)

pyz = PYZ(a.pure)
gui_exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VideoEditingAgent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
cli_exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VideoEditingAgent-cli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
updater_exe = EXE(
    updater_pyz,
    updater_a.scripts,
    updater_a.binaries,
    updater_a.datas,
    [],
    exclude_binaries=False,
    name="VideoEditingAgent-updater",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
coll = COLLECT(
    gui_exe,
    cli_exe,
    updater_exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="VideoEditingAgent",
)
