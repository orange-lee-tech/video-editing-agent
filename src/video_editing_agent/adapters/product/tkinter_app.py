from __future__ import annotations

import os
import queue
import threading
import time
import webbrowser
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any

from video_editing_agent.adapters.product.api_settings import (
    ApiCapabilitySettings,
    apply_settings_to_environment,
    settings_from_environment,
)
from video_editing_agent.adapters.product.appearance_settings import (
    AppearanceMode,
    AppearancePreferences,
    load_appearance_preferences,
    save_appearance_preferences,
)
from video_editing_agent.adapters.product.composition import editing_flow, planning_flow
from video_editing_agent.adapters.product.controller import (
    BriefForm,
    EditingForm,
    PlanningForm,
    PlanningSessionContext,
)
from video_editing_agent.adapters.product.presentation import (
    editing_presentation,
    planning_presentation,
    token_usage_presentation,
)
from video_editing_agent.adapters.product.runtime import resolve_product_runtime
from video_editing_agent.adapters.product.ui_components import create_brand_mark, recolor_brand_mark
from video_editing_agent.adapters.product.ui_theme import (
    DEFAULT_PRODUCT_TYPOGRAPHY,
    configure_product_theme,
    theme_tokens,
)
from video_editing_agent.adapters.product.update_check import UpdateCheckResult, check_for_update
from video_editing_agent.adapters.product.ux_support import (
    EtaEstimator,
    ProtectedCredentialStore,
    default_profile_root,
    delete_api_profile,
    format_eta,
    format_product_event,
    is_placeholder_value,
    load_api_profile,
    load_timing_history,
    localized_error,
    parse_profile,
    profile_filename,
    save_api_profile,
    save_timing_history,
    serialize_profile,
    write_utf8_export,
)
from video_editing_agent.adapters.product.workspace_ui import (
    BoundedFormHistory,
    OutputPathOwnership,
    WorkspaceFormStateStore,
    context_for_workspace,
    output_path_for_workspace,
    require_selected_workspace,
    restored_output_ownership,
)
from video_editing_agent.application.use_cases.product_flow import (
    OUTPUT_PROFILE_HORIZONTAL_1080P,
    OUTPUT_PROFILE_SQUARE_1080P,
    OUTPUT_PROFILE_VERTICAL_1080P,
    EditingOutputProfile,
    ProductFlowEvent,
    ProductFlowOutcome,
    VoiceMode,
)
from video_editing_agent.domain.edl.subtitle import SubtitleStyleProfile
from video_editing_agent.domain.shooting.model import ProductionConstraints
from video_editing_agent.providers.usage import set_thread_token_usage_sink
from video_editing_agent.storage.project.workspace import ProjectWorkspace
from video_editing_agent.system.windows_dpi import configure_tk_scaling
from video_editing_agent.version import APP_VERSION

_TEXT = {
    "zh-CN": {
        "window_title": "视频剪辑智能体",
        "app_title": "视频剪辑智能体",
        "app_subtitle": "AI Director + AI Video Editor",
        "tab_planning": "拍摄规划",
        "tab_editing": "自动剪辑",
        "planning_goal_title": "内容目标",
        "planning_reference_title": "参考与拍摄条件",
        "editing_goal_title": "成片目标",
        "editing_media_title": "素材与输出",
        "result_log_title": "结果与运行记录",
        "result_empty": "尚未生成结果。完成后会在这里显示可读摘要与运行记录。",
        "field_project": "项目目录",
        "workspace": "项目工作区",
        "workspace_unselected": "尚未选择项目工作区",
        "workspace_required": "请先选择项目工作区，再开始运行。",
        "configuration": "配置 ▾",
        "configuration_scope": "配置范围（可同时选择）",
        "form_configuration": "规划 / 剪辑表单",
        "api_configuration": "API / Provider",
        "import": "导入",
        "clear": "清空",
        "undo": "撤销",
        "redo": "重做",
        "output_exists_title": "确认覆盖输出",
        "output_exists_message": "所选输出文件已存在。是否明确覆盖该文件？",
        "field_title": "视频标题",
        "field_objective": "视频目标",
        "field_audience": "目标受众",
        "field_platform": "发布平台",
        "field_core_message": "核心信息",
        "field_authoritative_facts": "已确认事实",
        "field_reference_url": "参考视频 URL",
        "field_reference_local": "本地参考视频",
        "field_camera_or_phone": "拍摄设备",
        "field_production_notes": "拍摄备注",
        "field_media_files": "素材文件",
        "field_media_folder": "素材文件夹",
        "field_music_file": "背景音乐（可选）",
        "field_output_mp4": "输出视频",
        "field_output_profile": "成片规格",
        "field_subtitle_style": "字幕样式",
        "choose_project": "选择项目目录",
        "choose_local_reference": "选择本地参考视频",
        "start_planning": "开始生成拍摄方案",
        "choose_files": "选择素材文件",
        "choose_folder": "选择素材文件夹",
        "choose_music": "选择音乐",
        "music_rights_attestation": "仅本地音乐：我确认拥有将此音乐用于本成片所需的权利",
        "choose_output": "选择输出视频",
        "use_planning_result": "使用本次会话的拍摄规划结果",
        "start_editing": "开始自动剪辑",
        "planning_unavailable": "拍摄规划暂不可用",
        "editing_unavailable": "自动剪辑暂不可用",
        "editing_needs_attention": "自动剪辑需要处理",
        "editing_failed": "自动剪辑失败",
        "runtime_not_ready": "运行环境尚未就绪：",
        "dialog_choose_project": "选择或创建项目目录",
        "dialog_choose_reference": "选择本地参考视频",
        "dialog_choose_media": "选择本地素材文件",
        "dialog_choose_media_folder": "选择本地素材文件夹",
        "dialog_choose_music": "选择本地背景音乐",
        "dialog_choose_output": "选择最终视频输出位置",
        "filetype_audio": "常见音频文件",
        "filetype_video": "常见视频文件",
        "filetype_all": "所有文件",
        "switch_language": "English",
        "settings": "设置",
        "profiles": "配置文件",
        "settings_title": "配置与 API 设置",
        "settings_intro": "本软件不附赠 API 密钥。请使用你自己的 API 服务。",
        "settings_no_video": ("这些 API 仅用于理解、推理、规划和剪辑决策，不用于视频生成。"),
        "settings_session": ("当前 Stage A 仅在本次应用会话中使用密钥；不会写入项目、仓库或日志。"),
        "thinking_title": "思考指挥",
        "thinking_provider": "当前支持：DeepSeek",
        "thinking_usage": ("用于脚本规划、拍摄规划、方案复审，以及自动剪辑中的导演/编辑决策。"),
        "visual_title": "视觉理解",
        "visual_provider": "视觉 API 提供方",
        "visual_usage": ("用于理解参考视频和本地素材抽帧后的画面内容，为镜头选择提供语义证据。"),
        "visual_warning": (
            "允许两个能力位使用相同密钥；但视觉理解所对应的 API / 模型必须支持图像输入，"
            "否则素材分析会失败。"
        ),
        "api_key": "API 密钥",
        "save_settings": "应用设置",
        "cancel": "取消",
        "settings_applied": "API 设置已应用到本次会话。",
        "api_none": "API：未配置",
        "api_partial": "API：已配置 {count}/2",
        "api_complete": "API：2/2 已配置",
        "export": "导出",
        "file": "文件",
        "save": "保存",
        "save_as": "另存为",
        "load": "读取",
        "delete": "删除",
        "profile_saved": "配置已保存。",
        "profile_loaded": "配置已读取。",
        "profile_deleted": "配置已删除。",
        "profile_action_failed": "配置操作失败：{detail}",
        "selected_files": "已选择 {count} 个素材文件",
        "export_title": "导出当前输出",
        "exported": "已按 UTF-8 导出当前可见输出。",
        "estimating": "正在估算…",
        "running": "任务正在运行",
        "splash": "正在启动视频剪辑智能体…",
        "check_updates": "检查更新",
        "update_available_title": "发现新版本",
        "update_available_message": (
            "当前版本 v{current}\n最新版本 v{latest}\n\n是否打开更新下载页？"
        ),
        "up_to_date_title": "已是最新版本",
        "up_to_date_message": "当前版本 v{current} 已是最新版本。",
        "update_check_failed_title": "检查更新失败",
        "update_check_failed_message": "暂时无法检查更新：{detail}",
    },
    "en": {
        "window_title": "Video Editing Agent",
        "app_title": "Video Editing Agent",
        "app_subtitle": "AI Director + AI Video Editor",
        "tab_planning": "Planning",
        "tab_editing": "Editing",
        "planning_goal_title": "Content Goal",
        "planning_reference_title": "References & Filming",
        "editing_goal_title": "Edit Goal",
        "editing_media_title": "Media & Output",
        "result_log_title": "Result & Run Log",
        "result_empty": "No result yet. A readable summary and run log will appear here.",
        "field_project": "Project Directory",
        "workspace": "Project Workspace",
        "workspace_unselected": "No Project Workspace selected",
        "workspace_required": "Select a Project Workspace before starting.",
        "configuration": "Configuration ▾",
        "configuration_scope": "Configuration scope (select either or both)",
        "form_configuration": "Planning / Editing forms",
        "api_configuration": "API / Provider",
        "import": "Import",
        "clear": "Clear",
        "undo": "Undo",
        "redo": "Redo",
        "output_exists_title": "Confirm output overwrite",
        "output_exists_message": "The selected output file already exists. Overwrite it?",
        "field_title": "Video Title",
        "field_objective": "Objective",
        "field_audience": "Audience",
        "field_platform": "Platform",
        "field_core_message": "Core Message",
        "field_authoritative_facts": "Authoritative Facts",
        "field_reference_url": "Reference Video URL",
        "field_reference_local": "Local Reference Video",
        "field_camera_or_phone": "Camera or Phone",
        "field_production_notes": "Production Notes",
        "field_media_files": "Media Files",
        "field_media_folder": "Media Folder",
        "field_music_file": "Background Music (Optional)",
        "field_output_mp4": "Output Video",
        "field_output_profile": "Output Profile",
        "field_subtitle_style": "Subtitle Style",
        "choose_project": "Choose Project",
        "choose_local_reference": "Choose Local Reference",
        "start_planning": "Start Planning",
        "choose_files": "Choose Files",
        "choose_folder": "Choose Folder",
        "choose_music": "Choose Music",
        "music_rights_attestation": (
            "Local music only: I confirm I have the rights needed to use this music in this output"
        ),
        "choose_output": "Output Video",
        "use_planning_result": "Use Planning result from this session",
        "start_editing": "Start Editing",
        "planning_unavailable": "Planning unavailable",
        "editing_unavailable": "Editing unavailable",
        "editing_needs_attention": "Editing needs attention",
        "editing_failed": "Editing failed",
        "runtime_not_ready": "Runtime is not ready:",
        "dialog_choose_project": "Choose or create project directory",
        "dialog_choose_reference": "Choose local reference video",
        "dialog_choose_media": "Choose local media files",
        "dialog_choose_media_folder": "Choose local media folder",
        "dialog_choose_music": "Choose local background music",
        "dialog_choose_output": "Choose final video output",
        "filetype_audio": "Common audio files",
        "filetype_video": "Common video files",
        "filetype_all": "All files",
        "switch_language": "简体中文",
        "settings": "Settings",
        "profiles": "Profiles",
        "settings_title": "Configuration & API Settings",
        "settings_intro": (
            "This application does not include API keys. Use your own API services."
        ),
        "settings_no_video": (
            "These APIs are used only for understanding, reasoning, planning and editing "
            "decisions, not for video generation."
        ),
        "settings_session": (
            "Stage A uses keys only for this application session; they are not written to "
            "the project, repository or logs."
        ),
        "thinking_title": "Reasoning & Direction",
        "thinking_provider": "Currently supported: DeepSeek",
        "thinking_usage": (
            "Used for script planning, shooting planning, proposal review, and director/editorial "
            "decisions during automatic editing."
        ),
        "visual_title": "Visual Understanding",
        "visual_provider": "Visual API Provider",
        "visual_usage": (
            "Used to understand frames extracted from reference videos and local "
            "footage, producing semantic evidence for shot selection."
        ),
        "visual_warning": (
            "The same key may be entered for both capabilities, but the API/model used for Visual "
            "Understanding must support image input or media analysis will fail."
        ),
        "api_key": "API Key",
        "save_settings": "Apply Settings",
        "cancel": "Cancel",
        "settings_applied": "API settings were applied to this session.",
        "api_none": "API: not configured",
        "api_partial": "API: {count}/2 configured",
        "api_complete": "API: 2/2 configured",
        "export": "Export",
        "file": "File",
        "save": "Save",
        "save_as": "Save As",
        "load": "Load",
        "delete": "Delete",
        "profile_saved": "Profile saved.",
        "profile_loaded": "Profile loaded.",
        "profile_deleted": "Profile deleted.",
        "profile_action_failed": "Configuration action failed: {detail}",
        "selected_files": "{count} media files selected",
        "export_title": "Export visible output",
        "exported": "The visible output was exported as UTF-8.",
        "estimating": "Estimating…",
        "running": "Task is running",
        "splash": "Starting Video Editing Agent…",
        "check_updates": "Check for Updates",
        "update_available_title": "Update Available",
        "update_available_message": (
            "Current version v{current}\nLatest version v{latest}\n\nOpen the update download page?"
        ),
        "up_to_date_title": "Up to Date",
        "up_to_date_message": "Version v{current} is up to date.",
        "update_check_failed_title": "Update Check Failed",
        "update_check_failed_message": "Could not check for updates: {detail}",
    },
}


def validate_launcher_localizations() -> None:
    """Fail before constructing widgets when a launcher translation is incomplete."""

    expected = set(_TEXT["en"])
    for language, catalog in _TEXT.items():
        missing = expected - set(catalog)
        extra = set(catalog) - expected
        empty = tuple(key for key, value in catalog.items() if not value.strip())
        if missing or extra or empty:
            raise RuntimeError(
                f"launcher localization {language} is inconsistent: "
                f"missing={sorted(missing)}, extra={sorted(extra)}, empty={sorted(empty)}"
            )


_PLACEHOLDERS = {
    "zh-CN": {
        "project": "选择项目目录",
        "title": "例如：通勤小水瓶",
        "objective": "例如：说明为什么适合上班通勤",
        "audience": "例如：上班族",
        "platform": "例如：抖音",
        "core_message": "例如：小巧、方便",
        "authoritative_facts": "可选：容量 350mL（仅填写已确认事实）",
        "reference_url": "可选：公开视频 HTTPS 链接",
        "reference_local": "可选：本地参考视频",
        "camera_or_phone": "可选：例如手机",
        "production_notes": "可选：室内自然光、无需稳定器",
        "media_files": "选择一个或多个本地视频",
        "music_file": "留空则自动从公共素材库选择；或选择本地音频文件",
        "output_mp4": "选择最终视频输出位置",
    },
    "en": {
        "project": "Choose a project directory",
        "title": "e.g. Commuter Water Bottle",
        "objective": "e.g. explain why it is easy to carry",
        "audience": "e.g. commuters",
        "platform": "e.g. TikTok",
        "core_message": "e.g. compact and convenient",
        "authoritative_facts": "Optional — confirmed facts only, e.g. 350 mL",
        "reference_url": "Optional — public HTTPS video link",
        "reference_local": "Optional — local reference video",
        "camera_or_phone": "Optional — e.g. phone",
        "production_notes": "Optional — indoor natural light",
        "media_files": "Choose one or more local videos",
        "music_file": "Leave blank for public-library auto selection, or choose a local audio file",
        "output_mp4": "Choose final video destination",
    },
}


_OUTPUT_PROFILE_OPTIONS: tuple[tuple[str, EditingOutputProfile], ...] = (
    ("9:16 · 1080×1920 · 30 FPS", OUTPUT_PROFILE_VERTICAL_1080P),
    ("16:9 · 1920×1080 · 30 FPS", OUTPUT_PROFILE_HORIZONTAL_1080P),
    ("1:1 · 1080×1080 · 30 FPS", OUTPUT_PROFILE_SQUARE_1080P),
)


def _output_profile_for_display(value: str) -> EditingOutputProfile:
    for display, profile in _OUTPUT_PROFILE_OPTIONS:
        if display == value:
            return profile
    raise ValueError("Select a supported output profile")


def _display_for_output_profile_id(profile_id: str) -> str | None:
    for display, profile in _OUTPUT_PROFILE_OPTIONS:
        if profile.profile_id == profile_id:
            return display
    return None


def launch() -> int:
    validate_launcher_localizations()
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.withdraw()
    configure_product_theme(root)
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash.resizable(False, False)
    splash.geometry("430x120+420+280")
    splash_icon = tk.Canvas(
        splash,
        width=56,
        height=56,
        highlightthickness=0,
        borderwidth=0,
    )
    splash_icon.pack(pady=(14, 4))

    # Small dependency-free pixel mark: video frame + edit cut.
    pixel = 4
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
        splash_icon.create_rectangle(
            x1 * pixel,
            y1 * pixel,
            x2 * pixel,
            y2 * pixel,
            fill="#202020",
            outline="",
        )

    splash_label = ttk.Label(splash, text=_TEXT["zh-CN"]["splash"])
    splash_label.pack(padx=24, pady=(0, 10))
    splash_progress = ttk.Progressbar(splash, maximum=6, mode="determinate", length=360)
    splash_progress.pack(padx=24)
    splash.lift()
    splash.attributes("-topmost", True)
    splash.update()

    def startup_milestone(value: int) -> None:
        splash_progress.configure(value=value)
        splash.update()

    startup_milestone(1)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = min(900, max(720, int(screen_width * 0.55)))
    window_height = min(720, max(540, int(screen_height * 0.70)))
    # Fixed logical margins remain safe under Windows DPI virtualization, where centering
    # calculations can otherwise place the physical right edge beyond a laptop screen.
    window_x = 20
    window_y = 20
    root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
    root.minsize(min(720, window_width), min(540, window_height))
    language = tk.StringVar(value="zh-CN")
    startup_milestone(2)
    profile_root = default_profile_root()
    credential_store = ProtectedCredentialStore(profile_root)
    profile_root.mkdir(parents=True, exist_ok=True)
    timing_path = profile_root / "timing-history.json"
    timing_history = load_timing_history(timing_path)
    startup_milestone(3)
    api_settings = settings_from_environment(os.environ)
    current_api_profile: Path | None = None
    startup_milestone(4)

    def text(key: str) -> str:
        return _TEXT[language.get()][key]

    def api_status_text() -> str:
        configured = sum(
            bool(value.strip()) for value in (api_settings.thinking_key, api_settings.visual_key)
        )
        if configured == 0:
            return text("api_none")
        if configured == 2:
            return text("api_complete")
        return text("api_partial").format(count=configured)

    update_check_in_flight = False

    def finish_update_check(result: UpdateCheckResult, *, interactive: bool) -> None:
        nonlocal update_check_in_flight
        update_check_in_flight = False
        update_button.configure(state="normal")
        if result.update_available:
            manifest = result.manifest
            assert manifest is not None
            open_page = messagebox.askyesno(
                text("update_available_title"),
                text("update_available_message").format(
                    current=result.current_version,
                    latest=manifest.version,
                ),
                parent=root,
            )
            if open_page:
                webbrowser.open(manifest.download_url)
            return
        if not interactive:
            return
        if result.error is not None:
            messagebox.showwarning(
                text("update_check_failed_title"),
                text("update_check_failed_message").format(detail=result.error),
                parent=root,
            )
            return
        messagebox.showinfo(
            text("up_to_date_title"),
            text("up_to_date_message").format(current=result.current_version),
            parent=root,
        )

    def begin_update_check(interactive: bool = True) -> None:
        nonlocal update_check_in_flight
        if update_check_in_flight:
            return
        update_check_in_flight = True
        update_button.configure(state="disabled")

        def worker() -> None:
            result = check_for_update()
            root.after(0, lambda: finish_update_check(result, interactive=interactive))

        threading.Thread(target=worker, name="update-check", daemon=True).start()

    header = ttk.Frame(root, style="Header.TFrame", padding=(16, 9))
    header.pack(fill="x", padx=16, pady=(12, 6))

    brand_mark = create_brand_mark(header, size=38)
    brand_mark.pack(side="left", padx=(0, 10))

    identity = ttk.Frame(header, style="Header.TFrame")
    identity.pack(side="left", fill="y")
    app_title_label = ttk.Label(identity, style="AppTitle.TLabel")
    app_title_label.pack(anchor="w")
    app_subtitle_label = ttk.Label(identity, style="Muted.TLabel")
    app_subtitle_label.pack(anchor="w", pady=(2, 0))

    language_button = ttk.Button(header, style="Ghost.TButton")
    language_button.pack(side="right")
    update_button = ttk.Button(
        header,
        command=begin_update_check,
        style="Ghost.TButton",
    )
    update_button.pack(side="right", padx=(0, 4))
    configuration_button = ttk.Button(header, style="Ghost.TButton")
    configuration_button.pack(side="right", padx=(0, 4))
    api_status = ttk.Label(header, style="StatusPill.TLabel")
    api_status.pack(side="right", padx=(0, 10))

    workspace_bar = ttk.Frame(root, style="Header.TFrame", padding=(12, 8))
    workspace_bar.pack(fill="x", padx=16, pady=(0, 6))
    workspace_label = ttk.Label(workspace_bar, style="Body.TLabel")
    workspace_label.pack(side="left")
    workspace_value = tk.StringVar()
    workspace_entry = ttk.Entry(
        workspace_bar, textvariable=workspace_value, state="readonly", style="Product.TEntry"
    )
    workspace_entry.pack(side="left", fill="x", expand=True, padx=10)
    choose_workspace_button = ttk.Button(workspace_bar, style="Secondary.TButton")
    choose_workspace_button.pack(side="right")

    workflow_nav = ttk.Frame(root, style="Nav.TFrame")
    workflow_nav.pack(fill="x", padx=16, pady=(0, 4))

    notebook = ttk.Notebook(root, style="Product.TNotebook")
    notebook.pack(fill="both", expand=True, padx=16, pady=(0, 12))
    planning_page = ttk.Frame(notebook, style="App.TFrame")
    editing_page = ttk.Frame(notebook, style="App.TFrame")
    notebook.add(planning_page)
    notebook.add(editing_page)

    scroll_canvases: list[Any] = []

    def scrollable_page(page: Any) -> Any:
        canvas = tk.Canvas(page, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        content = ttk.Frame(canvas, style="App.TFrame", padding=(0, 8))
        window = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(window, width=event.width),
        )
        scroll_canvases.append(canvas)
        return content

    planning_tab = scrollable_page(planning_page)
    editing_tab = scrollable_page(editing_page)

    def scroll_active_page(event: Any) -> str | None:
        if getattr(event, "delta", 0) == 0:
            return None
        widget_class = event.widget.winfo_class()
        if widget_class in {"Text", "Listbox", "TCombobox"}:
            return None
        notebook_widget: Any = notebook
        selected = notebook_widget.index(notebook_widget.select())
        if selected >= len(scroll_canvases):
            return None
        scroll_canvases[selected].yview_scroll(-1 if event.delta > 0 else 1, "units")
        return "break"

    root.bind_all("<MouseWheel>", scroll_active_page, add="+")

    def select_workflow(target: str) -> None:
        is_planning = target == "planning"
        notebook.select(planning_page if is_planning else editing_page)  # type: ignore[no-untyped-call]
        planning_nav.configure(
            style="WorkflowActive.TButton" if is_planning else "Workflow.TButton"
        )
        editing_nav.configure(style="Workflow.TButton" if is_planning else "WorkflowActive.TButton")

    planning_nav = ttk.Button(
        workflow_nav,
        command=lambda: select_workflow("planning"),
        style="WorkflowActive.TButton",
    )
    planning_nav.pack(side="left")
    editing_nav = ttk.Button(
        workflow_nav,
        command=lambda: select_workflow("editing"),
        style="Workflow.TButton",
    )
    editing_nav.pack(side="left", padx=(4, 0))
    redo_button = ttk.Button(
        workflow_nav, command=lambda: mutate_history("redo"), style="Ghost.TButton"
    )
    redo_button.pack(side="right")
    undo_button = ttk.Button(
        workflow_nav, command=lambda: mutate_history("undo"), style="Ghost.TButton"
    )
    undo_button.pack(side="right", padx=(0, 4))
    clear_button = ttk.Button(
        workflow_nav, command=lambda: mutate_history("clear"), style="Ghost.TButton"
    )
    clear_button.pack(side="right", padx=(0, 4))

    field_labels: list[tuple[Any, str]] = []
    translated_widgets: list[tuple[Any, str]] = []
    translated_widgets.extend(
        ((clear_button, "clear"), (undo_button, "undo"), (redo_button, "redo"))
    )
    entry_fields: dict[int, tuple[Any, Any, str]] = {}

    def show_placeholder(entry: Any, value: Any, name: str) -> None:
        if not value.get().strip():
            value.set(_PLACEHOLDERS[language.get()][name])
            entry.configure(foreground="#777777")

    def field_value(value: Any) -> str:
        raw = value.get()
        return "" if is_placeholder_value(raw, _PLACEHOLDERS[language.get()]) else raw

    def set_field(value: Any, content: str) -> None:
        value.set(content)
        entry, _, name = entry_fields[id(value)]
        entry.configure(foreground="#000000")
        if not content:
            show_placeholder(entry, value, name)

    def clear_placeholder(_event: Any, entry: Any, value: Any) -> None:
        if is_placeholder_value(value.get(), _PLACEHOLDERS[language.get()]):
            value.set("")
            entry.configure(foreground="#000000")

    def restore_placeholder(_event: Any, entry: Any, value: Any, name: str) -> None:
        show_placeholder(entry, value, name)

    def fields(parent: Any, names: tuple[str, ...]) -> dict[str, Any]:
        values = {}
        for row, name in enumerate(names):
            label = ttk.Label(parent, style="Body.TLabel")
            label.grid(row=row, column=0, sticky="w", padx=(0, 12), pady=5)
            field_labels.append((label, name))
            value = tk.StringVar()
            entry = ttk.Entry(
                parent,
                textvariable=value,
                width=72,
                style="Product.TEntry",
            )
            entry.grid(row=row, column=1, sticky="ew", padx=0, pady=5)
            entry_fields[id(value)] = (entry, value, name)
            show_placeholder(entry, value, name)
            entry.bind(
                "<FocusIn>",
                partial(clear_placeholder, entry=entry, value=value),
            )
            entry.bind(
                "<FocusOut>",
                partial(restore_placeholder, entry=entry, value=value, name=name),
            )
            values[name] = value
        parent.columnconfigure(1, weight=1)
        return values

    collapsible_sections: list[tuple[Any, Any, str, Any]] = []

    def collapsible(parent: Any, row: int, title_key: str) -> Any:
        outer = ttk.Frame(parent, style="App.TFrame")
        outer.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        outer.columnconfigure(0, weight=1)
        body = ttk.Frame(outer, style="Card.TFrame", padding=12)
        expanded = tk.BooleanVar(value=True)
        header_button = ttk.Button(outer, style="Secondary.TButton")
        header_button.grid(row=0, column=0, sticky="ew")
        body.grid(row=1, column=0, sticky="ew")
        body.columnconfigure(1, weight=1)

        def toggle() -> None:
            expanded.set(not expanded.get())
            if expanded.get():
                body.grid()
            else:
                body.grid_remove()
            header_button.configure(text=("▾ " if expanded.get() else "▸ ") + text(title_key))

        header_button.configure(command=toggle)
        collapsible_sections.append((header_button, body, title_key, expanded))
        return body

    planning_goal_card = collapsible(planning_tab, 0, "planning_goal_title")
    planning_reference_card = collapsible(planning_tab, 1, "planning_reference_title")
    editing_goal_card = collapsible(editing_tab, 0, "editing_goal_title")
    editing_media_card = collapsible(editing_tab, 1, "editing_media_title")

    planning_tab.columnconfigure(0, weight=1)
    editing_tab.columnconfigure(0, weight=1)

    common_goal = ("title", "objective", "audience", "platform", "core_message")
    planning_values = fields(planning_goal_card, common_goal)
    planning_reference_values = fields(
        planning_reference_card,
        (
            "authoritative_facts",
            "reference_local",
            "camera_or_phone",
            "production_notes",
        ),
    )
    planning_values.update(planning_reference_values)

    editing_values = fields(editing_goal_card, common_goal)
    editing_media_values = fields(editing_media_card, ("media_files", "music_file", "output_mp4"))
    editing_values.update(editing_media_values)
    music_rights_attested = tk.BooleanVar(value=False)

    def reset_music_rights_on_path_change(*_args: object) -> None:
        music_rights_attested.set(False)

    editing_values["music_file"].trace_add("write", reset_music_rights_on_path_change)

    output_profile_label = ttk.Label(editing_media_card, style="Body.TLabel")
    output_profile_label.grid(row=4, column=0, sticky="w", padx=(0, 12), pady=5)
    field_labels.append((output_profile_label, "output_profile"))
    output_profile_choice = tk.StringVar(value=_OUTPUT_PROFILE_OPTIONS[0][0])
    output_profile_combo = ttk.Combobox(
        editing_media_card,
        textvariable=output_profile_choice,
        values=tuple(item[0] for item in _OUTPUT_PROFILE_OPTIONS),
        state="readonly",
        width=28,
        style="Product.TCombobox",
    )
    output_profile_combo.grid(row=4, column=1, sticky="ew", pady=5)

    # Stage A / 1.0 keeps subtitle styling fixed internally; advanced subtitle controls are 2.0.
    subtitle_style_choice = tk.StringVar(value=SubtitleStyleProfile.OUTLINED.value)

    planning_action_bar = ttk.Frame(planning_tab, style="App.TFrame")
    planning_action_bar.grid(row=2, column=0, sticky="ew", pady=(0, 8))
    planning_action_bar.columnconfigure(1, weight=1)

    editing_action_bar = ttk.Frame(editing_tab, style="App.TFrame")
    editing_action_bar.grid(row=2, column=0, sticky="ew", pady=(0, 8))
    editing_action_bar.columnconfigure(1, weight=1)

    result_frames: list[Any] = []

    def output_surface(parent: Any, row: int) -> tuple[Any, Any]:
        frame = ttk.LabelFrame(
            parent,
            style="Card.TLabelframe",
            padding=10,
        )
        frame.grid(row=row, column=0, sticky="nsew")
        parent.rowconfigure(row, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        result_frames.append(frame)
        output = tk.Text(
            frame,
            height=10,
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            background=DEFAULT_PRODUCT_THEME.surface,
            foreground=DEFAULT_PRODUCT_THEME.text_primary,
            insertbackground=DEFAULT_PRODUCT_THEME.text_primary,
            font=(
                DEFAULT_PRODUCT_TYPOGRAPHY.ui_family,
                DEFAULT_PRODUCT_TYPOGRAPHY.body_size,
            ),
        )
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=output.yview)
        output.configure(yscrollcommand=scrollbar.set)
        output.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        return output, frame

    planning_output, planning_output_frame = output_surface(planning_tab, 3)
    editing_output, editing_output_frame = output_surface(editing_tab, 3)
    planning_output.insert("1.0", text("result_empty"))
    editing_output.insert("1.0", text("result_empty"))
    current_form_profile: Path | None = None
    history_applying = False
    planning_context: PlanningSessionContext | None = None
    use_planning = tk.BooleanVar(value=False)
    output_path_ownership = OutputPathOwnership.WORKSPACE_DEFAULT
    histories = {
        "planning": BoundedFormHistory.create({}),
        "editing": BoundedFormHistory.create({}),
    }

    def workflow_snapshot(workflow: str) -> dict[str, str]:
        fields_map = planning_values if workflow == "planning" else editing_values
        values = {name: field_value(variable) for name, variable in fields_map.items()}
        if workflow == "editing":
            values["output_profile"] = output_profile_choice.get()
            values["subtitle_style"] = subtitle_style_choice.get()
            values["music_rights_attested"] = "1" if music_rights_attested.get() else "0"
            values["use_planning"] = "0"
            values["_output_path_ownership"] = output_path_ownership.value
        return values

    def apply_workflow_snapshot(workflow: str, values: dict[str, str]) -> None:
        nonlocal history_applying, output_path_ownership
        history_applying = True
        try:
            fields_map = planning_values if workflow == "planning" else editing_values
            for name, variable in fields_map.items():
                set_field(variable, values.get(name, ""))
            if workflow == "editing":
                output_profile_choice.set(
                    values.get("output_profile", _OUTPUT_PROFILE_OPTIONS[0][0])
                )
                subtitle_style_choice.set(SubtitleStyleProfile.OUTLINED.value)
                music_rights_attested.set(values.get("music_rights_attested") == "1")
                output_path_ownership = restored_output_ownership(
                    values.get("_output_path_ownership"),
                    values.get("output_mp4", ""),
                    ProjectWorkspace.open(
                        require_selected_workspace(workspace_value.get())
                    ).writable,
                )
                # Combined Planning -> Editing remains internal/deferred for the 1.0 ordinary UI.
                use_planning.set(False)
        finally:
            history_applying = False

    def persist_history(workflow: str) -> None:
        if not workspace_value.get().strip():
            return
        workspace = ProjectWorkspace.open(Path(workspace_value.get()))
        WorkspaceFormStateStore(workspace.writable, workflow).save(histories[workflow])

    def record_history(workflow: str) -> None:
        if history_applying:
            return
        if histories[workflow].record(workflow_snapshot(workflow)):
            persist_history(workflow)

    def active_workflow() -> str:
        selected = notebook.select()  # type: ignore[no-untyped-call]
        return "planning" if notebook.index(selected) == 0 else "editing"  # type: ignore[no-untyped-call]

    def mutate_history(action: str) -> None:
        if active_task is not None:
            return
        workflow = active_workflow()
        record_history(workflow)
        history = histories[workflow]
        if action == "clear":
            cleared = {key: "" for key in workflow_snapshot(workflow)}
            if workflow == "editing":
                cleared.update(
                    {
                        "output_profile": _OUTPUT_PROFILE_OPTIONS[0][0],
                        "subtitle_style": SubtitleStyleProfile.OUTLINED.value,
                        "music_rights_attested": "0",
                        "use_planning": "0",
                        "_output_path_ownership": OutputPathOwnership.WORKSPACE_DEFAULT.value,
                    }
                )
            history.record(cleared)
            apply_workflow_snapshot(workflow, cleared)
        else:
            restored = history.undo() if action == "undo" else history.redo()
            if restored is not None:
                apply_workflow_snapshot(workflow, restored)
        persist_history(workflow)

    def open_workspace(path: Path, *, restore: bool) -> None:
        nonlocal planning_context, output_path_ownership
        if active_task is not None:
            return
        if workspace_value.get().strip():
            for workflow in ("planning", "editing"):
                record_history(workflow)
                persist_history(workflow)
        workspace = ProjectWorkspace.open(path)
        workspace_value.set(str(workspace.root))
        planning_context = context_for_workspace(planning_context, workspace.root)
        use_planning.set(False)
        for workflow in ("planning", "editing"):
            loaded = WorkspaceFormStateStore(workspace.writable, workflow).load()
            if restore and loaded is not None:
                histories[workflow] = loaded
                apply_workflow_snapshot(workflow, loaded.current)
            else:
                snapshot = workflow_snapshot(workflow)
                histories[workflow] = BoundedFormHistory.create(snapshot)
        if output_path_ownership is OutputPathOwnership.WORKSPACE_DEFAULT:
            set_field(
                editing_values["output_mp4"],
                str(
                    output_path_for_workspace(
                        field_value(editing_values["output_mp4"]),
                        output_path_ownership,
                        workspace.writable,
                    )
                ),
            )
            histories["editing"].record(workflow_snapshot("editing"))
        for workflow in ("planning", "editing"):
            persist_history(workflow)

    def choose_workspace() -> None:
        selected = filedialog.askdirectory(title=text("dialog_choose_project"), mustexist=False)
        if selected:
            open_workspace(Path(selected), restore=True)

    choose_workspace_button.configure(command=choose_workspace)

    def form_profile_values() -> dict[str, str]:
        values: dict[str, str] = {}
        if workspace_value.get().strip():
            values["workspace"] = workspace_value.get().strip()
        for prefix, fields_map in (("planning", planning_values), ("editing", editing_values)):
            for name, variable in fields_map.items():
                actual = field_value(variable).strip()
                if actual:
                    values[f"{prefix}.{name}"] = actual
        values["editing.output_profile"] = _output_profile_for_display(
            output_profile_choice.get()
        ).profile_id
        values["editing._output_path_ownership"] = output_path_ownership.value
        return values

    def save_form_profile(*, choose: bool) -> None:
        nonlocal current_form_profile
        destination = current_form_profile
        if choose or destination is None:
            selected = filedialog.asksaveasfilename(
                title=text("save_as"),
                initialdir=profile_root,
                initialfile=profile_filename("form"),
                defaultextension=".txt",
                filetypes=(("Text", "*.txt"),),
            )
            if not selected:
                return
            destination = Path(selected)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialize_profile("form", form_profile_values()), encoding="utf-8")
        current_form_profile = destination
        messagebox.showinfo(text("file"), text("profile_saved"), parent=root)

    def load_form_profile() -> None:
        nonlocal current_form_profile, output_path_ownership
        selected = filedialog.askopenfilename(
            title=text("load"), initialdir=profile_root, filetypes=(("Text", "*.txt"),)
        )
        if not selected:
            return
        source = Path(selected)
        loaded = parse_profile(source.read_text(encoding="utf-8"), "form")
        loaded_workspace = loaded.get("workspace", "").strip()
        if loaded_workspace:
            open_workspace(Path(loaded_workspace), restore=True)
        for prefix, fields_map in (("planning", planning_values), ("editing", editing_values)):
            for name, variable in fields_map.items():
                set_field(variable, loaded.get(f"{prefix}.{name}", ""))
        loaded_output = loaded.get("editing.output_mp4", "")
        stored_ownership = loaded.get("editing._output_path_ownership")
        if workspace_value.get().strip():
            output_path_ownership = restored_output_ownership(
                stored_ownership,
                loaded_output,
                ProjectWorkspace.open(require_selected_workspace(workspace_value.get())).writable,
            )
        elif loaded_output.strip():
            output_path_ownership = OutputPathOwnership.EXPLICIT
        else:
            output_path_ownership = OutputPathOwnership.WORKSPACE_DEFAULT
        music_rights_attested.set(False)
        saved_output_profile = loaded.get("editing.output_profile")
        if saved_output_profile:
            display = _display_for_output_profile_id(saved_output_profile)
            if display is not None:
                output_profile_choice.set(display)
        current_form_profile = source
        messagebox.showinfo(text("file"), text("profile_loaded"), parent=root)

    def delete_form_profile() -> None:
        nonlocal current_form_profile
        selected = filedialog.askopenfilename(
            title=text("delete"), initialdir=profile_root, filetypes=(("Text", "*.txt"),)
        )
        if selected:
            Path(selected).unlink(missing_ok=True)
            if current_form_profile == Path(selected):
                current_form_profile = None
            messagebox.showinfo(text("file"), text("profile_deleted"), parent=root)

    def update_language() -> None:
        root.title(f"{text('window_title')} · v{APP_VERSION}")
        planning_nav.configure(text=text("tab_planning"))
        editing_nav.configure(text=text("tab_editing"))
        for label, name in field_labels:
            label.configure(text=text(f"field_{name}"))
        for widget, key in translated_widgets:
            widget.configure(text=text(key))
        app_title_label.configure(text=text("app_title"))
        app_subtitle_label.configure(text=f"{text('app_subtitle')} · v{APP_VERSION}")
        for header_button, _body, title_key, expanded in collapsible_sections:
            header_button.configure(text=("▾ " if expanded.get() else "▸ ") + text(title_key))
        for frame in result_frames:
            frame.configure(text=text("result_log_title"))
        language_button.configure(text=text("switch_language"))
        workspace_label.configure(text=text("workspace"))
        choose_workspace_button.configure(text=text("choose_project"))
        configuration_button.configure(text=text("configuration"))
        update_button.configure(text=text("check_updates"))
        api_status.configure(text=api_status_text())

    def toggle_language() -> None:
        old_language = language.get()
        language.set("en" if old_language == "zh-CN" else "zh-CN")
        for entry, value, name in entry_fields.values():
            if value.get() == _PLACEHOLDERS[old_language][name]:
                value.set("")
                show_placeholder(entry, value, name)
        update_language()

    language_button.configure(command=toggle_language)

    def open_settings() -> None:
        nonlocal api_settings, current_api_profile
        dialog = tk.Toplevel(root)
        dialog.title(text("settings_title"))
        dialog.geometry("680x650")
        dialog.transient(root)
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)

        ttk.Label(dialog, text=text("settings_intro"), wraplength=610).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 4)
        )
        ttk.Label(dialog, text=text("settings_no_video"), wraplength=610).grid(
            row=1, column=0, sticky="w", padx=18, pady=4
        )
        ttk.Label(dialog, text=text("settings_session"), wraplength=610).grid(
            row=2, column=0, sticky="w", padx=18, pady=(4, 14)
        )

        thinking = ttk.LabelFrame(dialog, text=text("thinking_title"))
        thinking.grid(row=3, column=0, sticky="ew", padx=18, pady=8)
        thinking.columnconfigure(1, weight=1)
        ttk.Label(thinking, text=text("thinking_provider")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 4)
        )
        ttk.Label(thinking, text=text("thinking_usage"), wraplength=580).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=10, pady=4
        )
        ttk.Label(thinking, text=text("api_key")).grid(
            row=2, column=0, sticky="w", padx=10, pady=(8, 10)
        )
        thinking_key = tk.StringVar(value=api_settings.thinking_key)
        ttk.Entry(thinking, textvariable=thinking_key, show="•", width=60).grid(
            row=2, column=1, sticky="ew", padx=(4, 10), pady=(8, 10)
        )

        visual = ttk.LabelFrame(dialog, text=text("visual_title"))
        visual.grid(row=4, column=0, sticky="ew", padx=18, pady=8)
        visual.columnconfigure(1, weight=1)
        ttk.Label(visual, text=text("visual_usage"), wraplength=580).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 4)
        )
        ttk.Label(visual, text=text("visual_provider")).grid(
            row=1, column=0, sticky="w", padx=10, pady=6
        )
        visual_provider = tk.StringVar(value=api_settings.visual_provider.capitalize())
        ttk.Combobox(
            visual,
            textvariable=visual_provider,
            values=("Gemini", "OpenAI"),
            state="readonly",
            width=16,
        ).grid(row=1, column=1, sticky="w", padx=(4, 10), pady=6)
        ttk.Label(visual, text=text("api_key")).grid(row=2, column=0, sticky="w", padx=10, pady=6)
        visual_key = tk.StringVar(value=api_settings.visual_key)
        ttk.Entry(visual, textvariable=visual_key, show="•", width=60).grid(
            row=2, column=1, sticky="ew", padx=(4, 10), pady=6
        )
        ttk.Label(visual, text=text("visual_warning"), wraplength=580).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 10)
        )

        profiles = ttk.LabelFrame(dialog, text=text("profiles"))
        profiles.grid(row=5, column=0, sticky="ew", padx=18, pady=8)
        profiles.columnconfigure(1, weight=1)

        buttons = ttk.Frame(dialog)
        buttons.grid(row=6, column=0, sticky="e", padx=18, pady=16)

        def save_settings() -> None:
            nonlocal api_settings
            api_settings = ApiCapabilitySettings(
                thinking_key=thinking_key.get(),
                visual_key=visual_key.get(),
                visual_provider=visual_provider.get().casefold(),
            )
            apply_settings_to_environment(api_settings, os.environ)
            api_status.configure(text=api_status_text())
            dialog.destroy()
            messagebox.showinfo(text("settings_title"), text("settings_applied"), parent=root)

        def save_api_file(*, choose: bool) -> None:
            nonlocal current_api_profile
            destination = current_api_profile
            if choose or destination is None:
                selected = filedialog.asksaveasfilename(
                    title=text("save_as"),
                    initialdir=profile_root,
                    initialfile=profile_filename("api"),
                    defaultextension=".txt",
                    filetypes=(("Text", "*.txt"),),
                    parent=dialog,
                )
                if not selected:
                    return
                destination = Path(selected)
            save_api_profile(
                destination,
                visual_provider=visual_provider.get().casefold(),
                thinking_key=thinking_key.get(),
                visual_key=visual_key.get(),
                credentials=credential_store,
            )
            current_api_profile = destination
            messagebox.showinfo(text("settings_title"), text("profile_saved"), parent=dialog)

        def load_api_file() -> None:
            nonlocal current_api_profile
            selected = filedialog.askopenfilename(
                title=text("load"),
                initialdir=profile_root,
                filetypes=(("Text", "*.txt"),),
                parent=dialog,
            )
            if not selected:
                return
            provider, thinking_secret, visual_secret = load_api_profile(
                Path(selected), credential_store
            )
            visual_provider.set(provider.capitalize())
            thinking_key.set(thinking_secret)
            visual_key.set(visual_secret)
            current_api_profile = Path(selected)
            messagebox.showinfo(text("settings_title"), text("profile_loaded"), parent=dialog)

        def delete_api_file() -> None:
            nonlocal current_api_profile
            selected = filedialog.askopenfilename(
                title=text("delete"),
                initialdir=profile_root,
                filetypes=(("Text", "*.txt"),),
                parent=dialog,
            )
            if selected:
                delete_api_profile(Path(selected), credential_store)
                if current_api_profile == Path(selected):
                    current_api_profile = None
                messagebox.showinfo(text("settings_title"), text("profile_deleted"), parent=dialog)

        def run_profile_action(action: Any) -> None:
            try:
                action()
            except Exception as exc:
                messagebox.showerror(
                    text("settings_title"),
                    text("profile_action_failed").format(detail=str(exc)),
                    parent=dialog,
                )

        profile_rows = (
            (
                "form_configuration",
                (
                    ("import", load_form_profile),
                    ("export", lambda: save_form_profile(choose=True)),
                    ("save", lambda: save_form_profile(choose=False)),
                    ("delete", delete_form_profile),
                ),
            ),
            (
                "api_configuration",
                (
                    ("import", load_api_file),
                    ("export", lambda: save_api_file(choose=True)),
                    ("save", lambda: save_api_file(choose=False)),
                    ("delete", delete_api_file),
                ),
            ),
        )
        for row, (label_key, actions) in enumerate(profile_rows):
            ttk.Label(profiles, text=text(label_key)).grid(
                row=row, column=0, sticky="w", padx=10, pady=8
            )
            action_frame = ttk.Frame(profiles)
            action_frame.grid(row=row, column=1, sticky="w", padx=(8, 10), pady=8)
            for action_key, action in actions:
                ttk.Button(
                    action_frame,
                    text=text(action_key),
                    command=partial(run_profile_action, action),
                ).pack(side="left", padx=(0, 6))

        ttk.Button(buttons, text=text("cancel"), command=dialog.destroy).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(buttons, text=text("save_settings"), command=save_settings).pack(side="right")

    configuration_button.configure(command=open_settings)

    work_queue: queue.Queue[tuple[str, str, Any]] = queue.Queue()
    active_task: str | None = None
    stage_started = time.monotonic()
    active_stage: ProductFlowEvent | None = None

    planning_eta = ttk.Label(planning_action_bar, text=text("estimating"), style="Status.TLabel")
    planning_eta.grid(row=0, column=0, sticky="w")
    editing_eta = ttk.Label(editing_action_bar, text=text("estimating"), style="Status.TLabel")
    editing_eta.grid(row=0, column=0, sticky="w")

    def show_event(widget: Any, event: ProductFlowEvent) -> None:
        widget.insert("end", format_product_event(event, language.get()) + "\n")
        widget.see("end")

    def update_eta(label: Any, event: ProductFlowEvent | None, workload: int) -> None:
        estimate = None
        if event is not None:
            estimate = EtaEstimator(timing_history, datetime.now().astimezone()).estimate(
                event.stage,
                workload=workload if event.stage.value == "ingest_understanding" else 1,
            )
        label.configure(text=format_eta(estimate, language.get()))

    def set_running(running: bool) -> None:
        execution_state = "disabled" if running else "normal"
        start_planning.configure(state=execution_state)
        start_editing.configure(state=execution_state)
        configuration_button.configure(state=execution_state)
        choose_workspace_button.configure(state=execution_state)

        # Each task runs from the immutable form/request snapshot captured at Start.
        # Keep the form editable so users can prepare the next run while background work continues.
        output_profile_combo.configure(state="readonly")
        music_rights_check.configure(state="normal")
        clear_button.configure(state="normal")
        undo_button.configure(state="normal")
        redo_button.configure(state="normal")
        for entry, _value, _name in entry_fields.values():
            entry.configure(state="normal")
        for widget in (choose_reference, choose_files, choose_music, choose_output):
            widget.configure(state="normal")

    def pump_work() -> None:
        nonlocal active_task, active_stage, stage_started, planning_context
        try:
            while True:
                task, kind, payload = work_queue.get_nowait()
                output = planning_output if task == "planning" else editing_output
                eta = planning_eta if task == "planning" else editing_eta
                if kind == "usage":
                    output.insert(
                        "end",
                        token_usage_presentation(payload, language.get()) + "\n",
                    )
                    output.see("end")
                elif kind == "event":
                    now = time.monotonic()
                    if active_stage is not None:
                        elapsed = max(0.001, now - stage_started)
                        previous = timing_history.get(active_stage.stage.value)
                        timing_history[active_stage.stage.value] = (
                            elapsed if previous is None else (previous * 0.7 + elapsed * 0.3)
                        )
                    stage_started = now
                    active_stage = payload
                    show_event(output, payload)
                    update_eta(eta, payload, 1)
                elif kind == "done":
                    result = payload
                    if task == "planning":
                        planning_context = PlanningSessionContext.from_result(result)
                        use_planning.set(False)
                        output.insert("end", "\n" + planning_presentation(result, language.get()))
                    else:
                        summary = editing_presentation(result, language.get())
                        output.insert("end", "\n" + summary)
                        if result.outcome is ProductFlowOutcome.CORRECTION_REQUIRED:
                            messagebox.showwarning(
                                text("editing_needs_attention"),
                                summary,
                                parent=root,
                            )
                        elif result.outcome is ProductFlowOutcome.FAILED:
                            messagebox.showerror(text("editing_failed"), summary, parent=root)
                    save_timing_history(timing_path, timing_history)
                    active_task = None
                    active_stage = None
                    set_running(False)
                    eta.configure(text="")
                elif kind == "error":
                    primary, detail = localized_error(payload, language.get())
                    messagebox.showerror(
                        text("planning_unavailable")
                        if task == "planning"
                        else text("editing_unavailable"),
                        primary + (f"\n\n{detail}" if detail else ""),
                        parent=root,
                    )
                    active_task = None
                    active_stage = None
                    set_running(False)
                    eta.configure(text="")
        except queue.Empty:
            pass
        root.after(100, pump_work)

    def refresh_eta() -> None:
        if active_task is not None:
            label = planning_eta if active_task == "planning" else editing_eta
            update_eta(label, active_stage, 1)
        root.after(30_000, refresh_eta)

    def brief(values: dict[str, Any]) -> BriefForm:
        return BriefForm(
            field_value(values["title"]),
            field_value(values["objective"]),
            field_value(values["audience"]),
            field_value(values["platform"]),
            field_value(values["core_message"]),
            tuple(item.strip() for item in field_value(values["authoritative_facts"]).splitlines())
            if "authoritative_facts" in values
            else (),
        )

    def run_planning() -> None:
        nonlocal active_task, stage_started
        if active_task is not None:
            return
        try:
            project = require_selected_workspace(workspace_value.get())
            # Remote reference observation is deferred until a video-native/provider-neutral
            # capability is available. Keep the ordinary product surface fail-closed meanwhile.
            reference_url = None
            local_reference_text = field_value(planning_values["reference_local"]).strip()
            has_reference = reference_url is not None or bool(local_reference_text)
            form = PlanningForm(
                project,
                brief(planning_values),
                ProductionConstraints(
                    camera_or_phone=(
                        field_value(planning_values["camera_or_phone"]).strip() or None
                    ),
                    notes=tuple(
                        item.strip()
                        for item in field_value(planning_values["production_notes"]).splitlines()
                        if item.strip()
                    ),
                ),
                reference_url=reference_url,
                local_reference=(Path(local_reference_text) if local_reference_text else None),
            )
            form.to_request()
            planning_output.delete("1.0", "end")
            active_task = "planning"
            stage_started = time.monotonic()
            set_running(True)
            planning_eta.configure(text=text("estimating"))

            def worker() -> None:
                previous_usage_sink = set_thread_token_usage_sink(
                    lambda usage: work_queue.put(("planning", "usage", usage))
                )
                try:
                    resolution = resolve_product_runtime(
                        mode="planning", reference_required=has_reference
                    )
                    if not resolution.is_ready or resolution.config is None:
                        raise RuntimeError("\n".join(resolution.diagnostics))
                    flow = planning_flow(form.project, resolution.config, reference=has_reference)
                    result = flow.run(
                        form.to_request(),
                        lambda event: work_queue.put(("planning", "event", event)),
                    )
                    work_queue.put(("planning", "done", result))
                except Exception as exc:
                    work_queue.put(("planning", "error", exc))
                finally:
                    set_thread_token_usage_sink(previous_usage_sink)

            threading.Thread(target=worker, name="planning-product-flow", daemon=True).start()
        except Exception as exc:
            primary, detail = localized_error(exc, language.get())
            if not workspace_value.get().strip():
                primary, detail = text("planning_unavailable"), text("workspace_required")
            messagebox.showerror(text("planning_unavailable"), primary + "\n\n" + detail)

    def run_editing() -> None:
        nonlocal active_task, stage_started
        if active_task is not None:
            return
        try:
            project = require_selected_workspace(workspace_value.get())
            raw_files = tuple(
                Path(item.strip())
                for item in field_value(editing_values["media_files"]).split(";")
                if item.strip()
            )
            music_text = field_value(editing_values["music_file"]).strip()
            workspace = ProjectWorkspace.open(project)
            output_path = Path(field_value(editing_values["output_mp4"]))
            if output_path.exists():
                if output_path.parent.resolve() == workspace.writable.final_outputs:
                    output_path = workspace.writable.default_final_output(output_path.stem)
                    set_field(editing_values["output_mp4"], str(output_path))
                elif not messagebox.askyesno(
                    text("output_exists_title"), text("output_exists_message"), parent=root
                ):
                    return
            form = EditingForm(
                project,
                brief(editing_values),
                output_path,
                raw_files,
                use_planning_result=False,
                planning_context=None,
                output_profile=_output_profile_for_display(output_profile_choice.get()),
                music_file=Path(music_text) if music_text else None,
                music_rights_attested=music_rights_attested.get(),
                voice_mode=VoiceMode.ORIGINAL,
                subtitle_style=SubtitleStyleProfile.OUTLINED,
            )
            form.to_request()
            editing_output.delete("1.0", "end")
            active_task = "editing"
            stage_started = time.monotonic()
            set_running(True)
            editing_eta.configure(text=text("estimating"))

            def worker() -> None:
                previous_usage_sink = set_thread_token_usage_sink(
                    lambda usage: work_queue.put(("editing", "usage", usage))
                )
                try:
                    resolution = resolve_product_runtime(mode="editing")
                    if not resolution.is_ready or resolution.config is None:
                        raise RuntimeError("\n".join(resolution.diagnostics))
                    flow = editing_flow(form.project, resolution.config)
                    result = flow.run(
                        form.to_request(),
                        lambda event: work_queue.put(("editing", "event", event)),
                    )
                    work_queue.put(("editing", "done", result))
                except Exception as exc:
                    work_queue.put(("editing", "error", exc))
                finally:
                    set_thread_token_usage_sink(previous_usage_sink)

            threading.Thread(target=worker, name="editing-product-flow", daemon=True).start()
        except Exception as exc:
            primary, detail = localized_error(exc, language.get())
            if not workspace_value.get().strip():
                primary, detail = text("editing_unavailable"), text("workspace_required")
            messagebox.showerror(text("editing_unavailable"), primary + "\n\n" + detail)

    choose_reference = ttk.Button(
        planning_reference_card,
        command=lambda: planning_values["reference_local"].set(
            filedialog.askopenfilename(title=text("dialog_choose_reference"))
        ),
        style="Secondary.TButton",
    )
    choose_reference.grid(row=2, column=2, padx=(10, 0))
    translated_widgets.append((choose_reference, "choose_local_reference"))

    start_planning = ttk.Button(
        planning_action_bar,
        command=run_planning,
        style="Primary.TButton",
    )
    start_planning.grid(row=0, column=2, sticky="e")
    translated_widgets.append((start_planning, "start_planning"))

    choose_files = ttk.Button(
        editing_media_card,
        command=lambda: choose_media_files(),
        style="Secondary.TButton",
    )
    choose_files.grid(row=0, column=2, padx=(10, 0))
    translated_widgets.append((choose_files, "choose_files"))

    selected_file_count = ttk.Label(editing_media_card, text="", style="Muted.TLabel")
    selected_file_count.grid(row=0, column=0, sticky="e", padx=(0, 12))

    def choose_media_files() -> None:
        selected = filedialog.askopenfilenames(title=text("dialog_choose_media"))
        if selected:
            set_field(editing_values["media_files"], ";".join(selected))
            selected_file_count.configure(text=text("selected_files").format(count=len(selected)))

    def choose_music_file() -> None:
        selected = filedialog.askopenfilename(
            title=text("dialog_choose_music"),
            filetypes=(
                (
                    text("filetype_audio"),
                    (
                        "*.mp3",
                        "*.wav",
                        "*.wave",
                        "*.flac",
                        "*.ogg",
                        "*.opus",
                        "*.m4a",
                        "*.aac",
                        "*.wma",
                    ),
                ),
                (text("filetype_all"), "*.*"),
            ),
        )
        if selected:
            set_field(editing_values["music_file"], selected)
            music_rights_attested.set(False)

    choose_music = ttk.Button(
        editing_media_card,
        command=choose_music_file,
        style="Secondary.TButton",
    )
    choose_music.grid(row=1, column=2, padx=(10, 0))
    translated_widgets.append((choose_music, "choose_music"))

    music_rights_check = ttk.Checkbutton(
        editing_media_card,
        variable=music_rights_attested,
        style="Product.TCheckbutton",
    )
    music_rights_check.grid(row=3, column=1, columnspan=2, sticky="w", pady=(6, 2))
    translated_widgets.append((music_rights_check, "music_rights_attestation"))

    def choose_output_path() -> None:
        nonlocal output_path_ownership
        selected = filedialog.asksaveasfilename(
            title=text("dialog_choose_output"),
            defaultextension=".mp4",
            filetypes=(
                (text("filetype_video"), ("*.mp4", "*.mov", "*.mkv", "*.webm")),
                (text("filetype_all"), "*.*"),
            ),
        )
        if selected:
            output_path_ownership = OutputPathOwnership.EXPLICIT
            set_field(editing_values["output_mp4"], selected)

    choose_output = ttk.Button(
        editing_media_card,
        command=choose_output_path,
        style="Secondary.TButton",
    )
    choose_output.grid(row=2, column=2, padx=(10, 0))
    translated_widgets.append((choose_output, "choose_output"))

    start_editing = ttk.Button(
        editing_action_bar,
        command=run_editing,
        style="Primary.TButton",
    )
    start_editing.grid(row=0, column=2, sticky="e")
    translated_widgets.append((start_editing, "start_editing"))

    def export_output(widget: Any) -> None:
        selected = filedialog.asksaveasfilename(
            title=text("export_title"),
            initialdir=Path.home() / "Desktop",
            defaultextension=".txt",
            filetypes=(("Text", "*.txt"),),
        )
        if selected:
            write_utf8_export(Path(selected), widget.get("1.0", "end-1c"))
            messagebox.showinfo(text("export_title"), text("exported"), parent=root)

    planning_export = ttk.Button(
        planning_action_bar,
        command=lambda: export_output(planning_output),
        style="Secondary.TButton",
    )
    planning_export.grid(row=0, column=1, sticky="e", padx=(0, 8))
    translated_widgets.append((planning_export, "export"))
    editing_export = ttk.Button(
        editing_action_bar,
        command=lambda: export_output(editing_output),
        style="Secondary.TButton",
    )
    editing_export.grid(row=0, column=1, sticky="e", padx=(0, 8))
    translated_widgets.append((editing_export, "export"))

    planning_variable_ids = {id(value) for value in planning_values.values()}
    for entry, value, _name in entry_fields.values():
        workflow = "planning" if id(value) in planning_variable_ids else "editing"
        entry.bind(
            "<FocusOut>",
            lambda _event, target=workflow: record_history(target),
            add="+",
        )
    output_profile_combo.bind(
        "<<ComboboxSelected>>", lambda _event: record_history("editing"), add="+"
    )
    root.bind_all("<Control-z>", lambda _event: mutate_history("undo"))
    root.bind_all("<Control-y>", lambda _event: mutate_history("redo"))
    root.bind_all("<Control-Shift-Z>", lambda _event: mutate_history("redo"))

    update_language()
    startup_milestone(5)
    root.update_idletasks()
    startup_milestone(6)
    splash.destroy()
    root.deiconify()
    pump_work()
    refresh_eta()
    if os.environ.get("VIDEO_EDITING_AGENT_LAUNCHER_SMOKE") == "1":
        smoke_workspace = os.environ.get("VIDEO_EDITING_AGENT_SMOKE_WORKSPACE", "").strip()
        if smoke_workspace:
            open_workspace(Path(smoke_workspace), restore=True)
        for header_button, _body, _title_key, _expanded in collapsible_sections:
            header_button.invoke()
            header_button.invoke()
        mutate_history("clear")
        mutate_history("undo")
        mutate_history("redo")
        configuration_button.invoke()
        root.update_idletasks()
        root.destroy()
        return 0
    root.after(1500, lambda: begin_update_check(False))
    root.mainloop()
    return 0
