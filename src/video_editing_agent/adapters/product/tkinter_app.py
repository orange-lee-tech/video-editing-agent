from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from video_editing_agent.adapters.product.composition import editing_flow, planning_flow
from video_editing_agent.adapters.product.controller import (
    BriefForm,
    EditingForm,
    PlanningForm,
)
from video_editing_agent.adapters.product.presentation import (
    editing_presentation,
    planning_presentation,
)
from video_editing_agent.adapters.product.runtime import resolve_product_runtime
from video_editing_agent.application.use_cases.product_flow import ProductFlowEvent
from video_editing_agent.domain.shooting.model import ProductionConstraints


def launch() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Video Editing Agent — Stage A")
    root.geometry("900x720")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    planning_tab, editing_tab = ttk.Frame(notebook), ttk.Frame(notebook)
    notebook.add(planning_tab, text="Planning")
    notebook.add(editing_tab, text="Editing")

    def fields(parent: Any, names: tuple[str, ...]) -> dict[str, Any]:
        values = {}
        for row, name in enumerate(names):
            ttk.Label(parent, text=name.replace("_", " ").title()).grid(
                row=row, column=0, sticky="w", padx=4, pady=3
            )
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

    def show_event(widget: Any, event: ProductFlowEvent) -> None:
        widget.insert("end", f"[{event.stage.value}] {event.message}\n")
        widget.see("end")
        root.update_idletasks()

    def choose_project(values: dict[str, Any]) -> None:
        selected = filedialog.askdirectory(mustexist=False)
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
        try:
            reference_url = planning_values["reference_url"].get().strip() or None
            local_reference_text = planning_values["reference_local"].get().strip()
            has_reference = reference_url is not None or bool(local_reference_text)
            resolution = resolve_product_runtime(mode="planning", reference_required=has_reference)
            if not resolution.is_ready or resolution.config is None:
                raise RuntimeError("\n".join(resolution.diagnostics))
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
            planning_output.insert("end", "\n" + planning_presentation(result))
        except Exception as exc:
            messagebox.showerror("Planning unavailable", str(exc))

    def run_editing() -> None:
        try:
            resolution = resolve_product_runtime(mode="editing")
            if not resolution.is_ready or resolution.config is None:
                raise RuntimeError("\n".join(resolution.diagnostics))
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
            )
            flow = editing_flow(form.project, resolution.config)
            editing_output.delete("1.0", "end")
            result = flow.run(form.to_request(), lambda event: show_event(editing_output, event))
            editing_output.insert("end", "\n" + editing_presentation(result))
        except Exception as exc:
            messagebox.showerror("Editing unavailable", str(exc))

    ttk.Button(
        planning_tab, text="Choose project", command=lambda: choose_project(planning_values)
    ).grid(row=0, column=2)
    ttk.Button(
        planning_tab,
        text="Choose local reference",
        command=lambda: planning_values["reference_local"].set(filedialog.askopenfilename()),
    ).grid(row=8, column=2)
    ttk.Button(planning_tab, text="Start Planning", command=run_planning).grid(
        row=11, column=1, sticky="e"
    )
    ttk.Button(
        editing_tab, text="Choose project", command=lambda: choose_project(editing_values)
    ).grid(row=0, column=2)
    ttk.Button(
        editing_tab,
        text="Choose files",
        command=lambda: editing_values["media_files"].set(";".join(filedialog.askopenfilenames())),
    ).grid(row=6, column=2)
    ttk.Button(
        editing_tab,
        text="Choose folder",
        command=lambda: editing_values["media_folder"].set(filedialog.askdirectory()),
    ).grid(row=7, column=2)
    ttk.Button(
        editing_tab,
        text="Output MP4",
        command=lambda: editing_values["output_mp4"].set(
            filedialog.asksaveasfilename(defaultextension=".mp4")
        ),
    ).grid(row=8, column=2)
    ttk.Button(editing_tab, text="Start Editing", command=run_editing).grid(
        row=10, column=1, sticky="e"
    )
    if os.environ.get("VIDEO_EDITING_AGENT_LAUNCHER_SMOKE") == "1":
        root.update_idletasks()
        root.destroy()
        return 0
    root.mainloop()
    return 0
