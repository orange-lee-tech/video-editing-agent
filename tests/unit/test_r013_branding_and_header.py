from pathlib import Path


def test_visible_brand_is_youqi_while_compatibility_identifiers_stay_stable() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")
    installer = Path("packaging/windows/VideoEditingAgent.iss").read_text(encoding="utf-8")

    assert '"app_title": "有岐"' in ui
    assert '"app_subtitle": "创作有岐，表达有路"' in ui
    assert '"window_title": "Youqi"' in ui
    assert '"app_title": "Youqi"' in ui
    assert '"app_subtitle": "Create your way, express your path"' in ui
    assert '"splash": "Starting Youqi…"' in ui
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
    assert "StatusPill.TLabel" not in header
    assert "api_status" not in header
    assert 'text("check_updates")' in ui
    assert "settings_update_button = ttk.Button" in ui


def test_declaration_uses_exact_product_owner_statement_and_one_ack_button() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    assert "来自开发者的声明：本软件制作的目标在于尝试一个兼容性良好的框架" in ui
    assert "在2027年以前我们会放上源代码链接" in ui
    assert "本声明是一个临时版本，后续也会更新" in ui
    declaration_start = ui.index("def open_declaration()")
    settings_start = ui.index("def open_settings()", declaration_start)
    declaration = ui[declaration_start:settings_start]
    assert declaration.count("ttk.Button(") == 1
    assert 'text("declaration_ack")' in declaration
    assert '"developer_homepage_closed": "开发者已经暂时关闭，2027年以前会打开"' in ui
    assert 'homepage.bind("<Button-1>", show_developer_homepage_notice)' in declaration
    assert 'webbrowser.open("https://github.com/orange-lee-tech")' not in declaration


def test_settings_keeps_profile_actions_visible_through_scrollable_container() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    settings_start = ui.index("def open_settings()")
    settings_end = ui.index("configuration_button.configure(command=open_settings)", settings_start)
    settings = ui[settings_start:settings_end]

    assert "settings_canvas = tk.Canvas(" in settings
    assert "settings_scrollbar = ttk.Scrollbar(" in settings
    assert 'dialog.bind("<MouseWheel>", scroll_settings, add="+")' in settings
    assert '("import", load_form_profile)' in settings
    assert '("export", lambda: save_form_profile(choose=True))' in settings
    assert '("save", lambda: save_form_profile(choose=False))' in settings
    assert '("delete", delete_form_profile)' in settings
    assert '("import", load_api_file)' in settings
    assert '("export", lambda: save_api_file(choose=True))' in settings
    assert '("save", lambda: save_api_file(choose=False))' in settings
    assert '("delete", delete_api_file)' in settings


def test_appearance_selection_previews_immediately_and_cancel_restores_previous_mode() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    settings_start = ui.index("def open_settings()")
    settings_end = ui.index("configuration_button.configure(command=open_settings)", settings_start)
    settings = ui[settings_start:settings_end]

    assert 'appearance_combo.bind("<<ComboboxSelected>>", preview_appearance)' in settings
    assert "apply_appearance(selected_mode, persist=False)" in settings
    assert "apply_appearance(original_appearance_mode, persist=False)" in settings
    assert 'dialog.protocol("WM_DELETE_WINDOW", cancel_settings)' in settings
    assert "apply_appearance(" in settings
    assert "persist=True" in settings


def test_appearance_refreshes_entry_foregrounds_including_placeholders() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    appearance_start = ui.index("def apply_appearance(")
    language_start = ui.index("def update_language()", appearance_start)
    appearance = ui[appearance_start:language_start]

    assert "for entry, value, name in entry_fields.values()" in appearance
    assert "current_theme.text_secondary" in appearance
    assert "current_theme.text_primary" in appearance
    assert "_PLACEHOLDERS[language.get()][name]" in appearance


def test_local_reference_picker_is_aligned_with_reference_field() -> None:
    ui = Path("src/video_editing_agent/adapters/product/tkinter_app.py").read_text(encoding="utf-8")

    assert 'choose_reference.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=5)' in ui
