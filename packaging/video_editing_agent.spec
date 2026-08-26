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
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VideoEditingAgent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="VideoEditingAgent",
)
