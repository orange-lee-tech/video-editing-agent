from __future__ import annotations

import os
from pathlib import Path
from typing import Any

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
)
from video_editing_agent.adapters.product.runtime import resolve_product_runtime
from video_editing_agent.application.use_cases.product_flow import ProductFlowEvent
from video_editing_agent.domain.shooting.model import ProductionConstraints

_TEXT = {
    "zh-CN": {
        "window_title": "视频剪辑智能体 — Stage A",
        "tab_planning": "拍摄规划",
        "tab_editing": "自动剪辑",
        "field_project": "项目目录",
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
        "field_output_mp4": "输出 MP4",
        "choose_project": "选择项目目录",
        "choose_local_reference": "选择本地参考视频",
        "start_planning": "开始生成拍摄方案",
        "choose_files": "选择素材文件",
        "choose_folder": "选择素材文件夹",
        "choose_output": "选择输出 MP4",
        "use_planning_result": "使用本次会话的拍摄规划结果",
        "start_editing": "开始自动剪辑",
        "planning_unavailable": "拍摄规划暂不可用",
        "editing_unavailable": "自动剪辑暂不可用",
        "runtime_not_ready": "运行环境尚未就绪：",
        "dialog_choose_project": "选择或创建项目目录",
        "dialog_choose_reference": "选择本地参考视频",
        "dialog_choose_media": "选择本地素材文件",
        "dialog_choose_media_folder": "选择本地素材文件夹",
        "dialog_choose_output": "选择最终 MP4 输出位置",
        "filetype_mp4": "MP4 视频",
        "filetype_all": "所有文件",
        "switch_language": "English",
    },
    "en": {
        "window_title": "Video Editing Agent — Stage A",
        "tab_planning": "Planning",
        "tab_editing": "Editing",
        "field_project": "Project Directory",
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
        "field_output_mp4": "Output MP4",
        "choose_project": "Choose Project",
        "choose_local_reference": "Choose Local Reference",
        "start_planning": "Start Planning",
        "choose_files": "Choose Files",
        "choose_folder": "Choose Folder",
        "choose_output": "Output MP4",
        "use_planning_result": "Use Planning result from this session",
        "start_editing": "Start Editing",
        "planning_unavailable": "Planning unavailable",
        "editing_unavailable": "Editing unavailable",
        "runtime_not_ready": "Runtime is not ready:",
        "dialog_choose_project": "Choose or create project directory",
        "dialog_choose_reference": "Choose local reference video",
        "dialog_choose_media": "Choose local media files",
        "dialog_choose_media_folder": "Choose local media folder",
        "dialog_choose_output": "Choose final MP4 output",
        "filetype_mp4": "MP4 video",
        "filetype_all": "All files",
        "switch_language": "简体中文",
    },
}


def launch() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.geometry("940x760")
    language = tk.StringVar(value="zh-CN")

    def text(key: str) -> str:
        return _TEXT[language.get()][key]

    header = ttk.Frame(root)
    header.pack(fill="x", padx=10, pady=(10, 0))
    language_button = ttk.Button(header)
    language_button.pack(side="right")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    planning_tab, editing_tab = ttk.Frame(notebook), ttk.Frame(notebook)
    notebook.add(planning_tab)
    notebook.add(editing_tab)

    field_labels: list[tuple[Any, str]] = []
    translated_widgets: list[tuple[Any, str]] = []

    def fields(parent: Any, names: tuple[str, ...]) -> dict[str, Any]:
        values = {}
        for row, name in enumerate(names):
            label = ttk.Label(parent)
            label.grid(row=row, column=0, sticky="w", padx=4, pady=3)
            field_labels.append((label, name))
            value = tk.StringVar()
            ttk.Entry(parent, textvariable=value, width=80).grid(
                row=row, column=1, sticky="ew", padx=4, pady=3
            )
            values[name] = value
        parent.columnconfigure(1, weight=1)
        return values

    common = ("project", "title", "objective", "audience", "platform", "core_message")
    planning_values = fields(
        planning_tab,
        (
            *common,
            "authoritative_facts",
            "reference_url",
            "reference_local",
            "camera_or_phone",
            "production_notes",
        ),
    )
    editing_values = fields(editing_tab, (*common, "media_files", "media_folder", "output_mp4"))
    planning_output = tk.Text(planning_tab, height=22, wrap="word")
    editing_output = tk.Text(editing_tab, height=22, wrap="word")
    planning_output.grid(row=12, column=0, columnspan=3, sticky="nsew")
    editing_output.grid(row=11, column=0, columnspan=3, sticky="nsew")
    planning_context: PlanningSessionContext | None = None
    use_planning = tk.BooleanVar(value=False)

    def update_language() -> None:
        root.title(text("window_title"))
        notebook.tab(planning_tab, text=text("tab_planning"))
        notebook.tab(editing_tab, text=text("tab_editing"))
        for label, name in field_labels:
            label.configure(text=text(f"field_{name}"))
        for widget, key in translated_widgets:
            widget.configure(text=text(key))
        language_button.configure(text=text("switch_language"))

    def toggle_language() -> None:
        language.set("en" if language.get() == "zh-CN" else "zh-CN")
        update_language()

    language_button.configure(command=toggle_language)

    def show_event(widget: Any, event: ProductFlowEvent) -> None:
        widget.insert("end", f"[{event.stage.value}] {event.message}\n")
        widget.see("end")
        root.update_idletasks()

    def choose_project(values: dict[str, Any]) -> None:
        selected = filedialog.askdirectory(title=text("dialog_choose_project"), mustexist=False)
        if selected:
            values["project"].set(selected)

    def brief(values: dict[str, Any]) -> BriefForm:
        return BriefForm(
            values["title"].get(),
            values["objective"].get(),
            values["audience"].get(),
            values["platform"].get(),
            values["core_message"].get(),
            tuple(item.strip() for item in values["authoritative_facts"].get().splitlines())
            if "authoritative_facts" in values
            else (),
        )

    def run_planning() -> None:
        nonlocal planning_context
        try:
            reference_url = planning_values["reference_url"].get().strip() or None
            local_reference_text = planning_values["reference_local"].get().strip()
            has_reference = reference_url is not None or bool(local_reference_text)
            resolution = resolve_product_runtime(mode="planning", reference_required=has_reference)
            if not resolution.is_ready or resolution.config is None:
                raise RuntimeError(text("runtime_not_ready") + "\n" + "\n".join(resolution.diagnostics))
            form = PlanningForm(
                Path(planning_values["project"].get()),
                brief(planning_values),
                ProductionConstraints(
                    camera_or_phone=(planning_values["camera_or_phone"].get().strip() or None),
                    notes=tuple(
                        item.strip()
                        for item in planning_values["production_notes"].get().splitlines()
                        if item.strip()
                    ),
                ),
                reference_url=reference_url,
                local_reference=(Path(local_reference_text) if local_reference_text else None),
            )
            flow = planning_flow(form.project, resolution.config, reference=has_reference)
            planning_output.delete("1.0", "end")
            result = flow.run(form.to_request(), lambda event: show_event(planning_output, event))
            planning_context = PlanningSessionContext.from_result(result)
            use_planning_check.configure(
                state="normal" if planning_context is not None else "disabled"
            )
            if planning_context is None:
                use_planning.set(False)
            planning_output.insert("end", "\n" + planning_presentation(result))
        except Exception as exc:
            messagebox.showerror(text("planning_unavailable"), str(exc))

    def run_editing() -> None:
        try:
            resolution = resolve_product_runtime(mode="editing")
            if not resolution.is_ready or resolution.config is None:
                raise RuntimeError(text("runtime_not_ready") + "\n" + "\n".join(resolution.diagnostics))
            raw_files = tuple(
                Path(item.strip())
                for item in editing_values["media_files"].get().split(";")
                if item.strip()
            )
            folder_text = editing_values["media_folder"].get().strip()
            form = EditingForm(
                Path(editing_values["project"].get()),
                brief(editing_values),
                Path(editing_values["output_mp4"].get()),
                raw_files,
                None if not folder_text else Path(folder_text),
                use_planning_result=use_planning.get(),
                planning_context=planning_context,
            )
            flow = editing_flow(form.project, resolution.config)
            editing_output.delete("1.0", "end")
            result = flow.run(form.to_request(), lambda event: show_event(editing_output, event))
            editing_output.insert("end", "\n" + editing_presentation(result))
        except Exception as exc:
            messagebox.showerror(text("editing_unavailable"), str(exc))

    choose_planning_project = ttk.Button(
        planning_tab, command=lambda: choose_project(planning_values)
    )
    choose_planning_project.grid(row=0, column=2)
    translated_widgets.append((choose_planning_project, "choose_project"))

    choose_reference = ttk.Button(
        planning_tab,
        command=lambda: planning_values["reference_local"].set(
            filedialog.askopenfilename(title=text("dialog_choose_reference"))
        ),
    )
    choose_reference.grid(row=8, column=2)
    translated_widgets.append((choose_reference, "choose_local_reference"))

    start_planning = ttk.Button(planning_tab, command=run_planning)
    start_planning.grid(row=11, column=1, sticky="e")
    translated_widgets.append((start_planning, "start_planning"))

    choose_editing_project = ttk.Button(
        editing_tab, command=lambda: choose_project(editing_values)
    )
    choose_editing_project.grid(row=0, column=2)
    translated_widgets.append((choose_editing_project, "choose_project"))

    choose_files = ttk.Button(
        editing_tab,
        command=lambda: editing_values["media_files"].set(
            ";".join(filedialog.askopenfilenames(title=text("dialog_choose_media")))
        ),
    )
    choose_files.grid(row=6, column=2)
    translated_widgets.append((choose_files, "choose_files"))

    choose_folder = ttk.Button(
        editing_tab,
        command=lambda: editing_values["media_folder"].set(
            filedialog.askdirectory(title=text("dialog_choose_media_folder"))
        ),
    )
    choose_folder.grid(row=7, column=2)
    translated_widgets.append((choose_folder, "choose_folder"))

    choose_output = ttk.Button(
        editing_tab,
        command=lambda: editing_values["output_mp4"].set(
            filedialog.asksaveasfilename(
                title=text("dialog_choose_output"),
                defaultextension=".mp4",
                filetypes=((text("filetype_mp4"), "*.mp4"), (text("filetype_all"), "*.*")),
            )
        ),
    )
    choose_output.grid(row=8, column=2)
    translated_widgets.append((choose_output, "choose_output"))

    use_planning_check = ttk.Checkbutton(
        editing_tab,
        variable=use_planning,
        state="disabled",
    )
    use_planning_check.grid(row=9, column=1, sticky="w")
    translated_widgets.append((use_planning_check, "use_planning_result"))

    start_editing = ttk.Button(editing_tab, command=run_editing)
    start_editing.grid(row=10, column=1, sticky="e")
    translated_widgets.append((start_editing, "start_editing"))

    update_language()
    if os.environ.get("VIDEO_EDITING_AGENT_LAUNCHER_SMOKE") == "1":
        root.update_idletasks()
        root.destroy()
        return 0
    root.mainloop()
    return 0
