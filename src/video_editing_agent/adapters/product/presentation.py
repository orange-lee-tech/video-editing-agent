from __future__ import annotations

from video_editing_agent.application.use_cases.product_flow import (
    EditingProductResult,
    PlanningProductResult,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def planning_presentation(result: PlanningProductResult, language: str = "en") -> str:
    zh = language == "zh-CN"
    if result.script_plan_ref is None or result.shooting_plan_ref is None:
        label = "拍摄规划" if zh else "Planning"
        fallback = "没有通过复审的方案" if zh else "no accepted plans"
        return f"{label} {result.outcome.value}: {result.diagnostic or fallback}"
    workspace = ProjectWorkspace.open(result.project_location)
    script = workspace.scripts.load(result.script_plan_ref)
    shooting = workspace.shooting_plans.load(result.shooting_plan_ref)
    lines = [
        f"{'脚本方案' if zh else 'ScriptPlan'} {script.envelope.id}@{script.envelope.revision}"
    ]
    for section in script.sections:
        lines.extend(
            (
                f"[{section.narrative_role}] {section.information_goal}",
                f"  {'口播' if zh else 'Spoken'}: {section.spoken_content or '-'}",
                f"  {'画面' if zh else 'Visual'}: {section.visual_requirement or '-'}",
                f"  {'时长' if zh else 'Timing'}: {section.target_duration or '-'}",
            )
        )
    lines.append(
        f"{'拍摄方案' if zh else 'ShootingPlan'} "
        f"{shooting.envelope.id}@{shooting.envelope.revision}"
    )
    resources = tuple(
        item
        for item in (
            shooting.constraints.camera_or_phone,
            shooting.constraints.stabilizer,
            shooting.constraints.lighting,
            *shooting.constraints.microphones,
        )
        if item
    )
    lines.append(
        ("拍摄资源：" if zh else "Production resources: ")
        + (", ".join(resources) if resources else "-")
    )
    for item in shooting.requirements:
        lines.extend(
            (
                f"[{item.requirement_id}] {item.purpose}",
                f"  {'拍摄' if zh else 'Capture'}: {item.capture_instruction or '-'}",
                f"  {'构图/运动' if zh else 'Framing/motion'}: "
                f"{item.framing or '-'} / {item.camera_motion or '-'}",
                f"  {'资源' if zh else 'Resources'}: {item.location_ref or '-'}",
            )
        )
    if shooting.notes:
        lines.append(("备注：" if zh else "Notes: ") + "; ".join(shooting.notes))
    return "\n".join(lines)


def editing_presentation(result: EditingProductResult, language: str = "en") -> str:
    zh = language == "zh-CN"
    if result.output_path is not None:
        return (
            f"{'已完成' if zh else 'Completed'}\n"
            f"{'最终 MP4' if zh else 'Final MP4'}: {result.output_path}"
        )
    if result.review_verdict is not None:
        return (
            f"{'复审' if zh else 'Review'}: {result.review_verdict.disposition.value}\n"
            f"{'修正路径' if zh else 'Correction'}: {result.review_verdict.correction_route.value}"
        )
    label = "自动剪辑" if zh else "Editing"
    fallback = "没有输出" if zh else "no output"
    return f"{label} {result.outcome.value}: {result.diagnostic or fallback}"
