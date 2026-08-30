from pathlib import Path


def test_visible_brand_is_youqi_while_compatibility_identifiers_stay_stable() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")
    installer = Path("packaging/windows/VideoEditingAgent.iss").read_text(encoding="utf-8")

    assert '"app_title": "有岐"' in ui
    assert '"app_subtitle": "创作有岐，表达有路"' in ui
    assert "app_subtitle_label.configure(text=f\"{text('app_subtitle')} · v{APP_VERSION}\")" in ui
    assert '#define AppName "有岐"' in installer
    assert 'Name: "{group}\\有岐"' in installer
    assert '#define AppExeName "VideoEditingAgent.exe"' in installer
    assert '#define AppId "{{9A3F2C7B-7C4D-4BA8-9E79-6D8C1C6B98A4}"' in installer
    assert "DefaultDirName={localappdata}\\Programs\\Video Editing Agent" in installer


def test_header_has_language_settings_declaration_but_no_standalone_update_button() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    header_start = ui.index('header = ttk.Frame(root, style="Header.TFrame"')
    workspace_start = ui.index("workspace_bar = ttk.Frame(", header_start)
    header = ui[header_start:workspace_start]

    assert "language_button = ttk.Button" in header
    assert "configuration_button = ttk.Button" in header
    assert "declaration_button = ttk.Button" in header
    assert "update_button = ttk.Button" not in header
    assert 'text("check_updates")' in ui
    assert "settings_update_button = ttk.Button" in ui


def test_declaration_uses_exact_product_owner_statement_and_one_ack_button() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(
        encoding="utf-8"
    )

    assert "来自开发者的声明：本软件制作的目标在于尝试一个兼容性良好的框架" in ui
    assert "在2027年以前我们会放上源代码链接" in ui
    assert "本声明是一个临时版本，后续也会更新" in ui
    declaration_start = ui.index("def open_declaration()")
    settings_start = ui.index("def open_settings()", declaration_start)
    declaration = ui[declaration_start:settings_start]
    assert declaration.count("ttk.Button(") == 1
    assert 'text("declaration_ack")' in declaration
    assert "https://github.com/orange-lee-tech" in declaration
