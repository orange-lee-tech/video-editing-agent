from __future__ import annotations

from video_editing_agent.application.use_cases.product_flow import (
    EditingProductResult,
    PlanningProductResult,
)
from video_editing_agent.storage.project.workspace import ProjectWorkspace


def planning_presentation(result: PlanningProductResult) -> str:
    if result.script_plan_ref is None or result.shooting_plan_ref is None:
        return f"Planning {result.outcome.value}: {result.diagnostic or 'no accepted plans'}"
    workspace = ProjectWorkspace.open(result.project_location)
    script = workspace.scripts.load(result.script_plan_ref)
    shooting = workspace.shooting_plans.load(result.shooting_plan_ref)
    lines = [f"ScriptPlan {script.envelope.id}@{script.envelope.revision}"]
    for section in script.sections:
        lines.extend(
            (
                f"[{section.narrative_role}] {section.information_goal}",
                f"  Spoken: {section.spoken_content or '-'}",
                f"  Visual: {section.visual_requirement or '-'}",
                f"  Timing: {section.target_duration or '-'}",
            )
        )
    lines.append(f"ShootingPlan {shooting.envelope.id}@{shooting.envelope.revision}")
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
    lines.append("Production resources: " + (", ".join(resources) if resources else "-"))
    for item in shooting.requirements:
        lines.extend(
            (
                f"[{item.requirement_id}] {item.purpose}",
                f"  Capture: {item.capture_instruction or '-'}",
                f"  Framing/motion: {item.framing or '-'} / {item.camera_motion or '-'}",
                f"  Resources: {item.location_ref or '-'}",
            )
        )
    if shooting.notes:
        lines.append("Notes: " + "; ".join(shooting.notes))
    return "\n".join(lines)


def editing_presentation(result: EditingProductResult) -> str:
    if result.output_path is not None:
        return f"Completed\nFinal MP4: {result.output_path}"
    if result.review_verdict is not None:
        return (
            f"Review: {result.review_verdict.disposition.value}\n"
            f"Correction: {result.review_verdict.correction_route.value}"
        )
    return f"Editing {result.outcome.value}: {result.diagnostic or 'no output'}"
