from __future__ import annotations

from fractions import Fraction

from video_editing_agent.application.use_cases.product_flow import (
    EditingProductResult,
    PlanningProductResult,
)
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.storage.project.workspace import ProjectWorkspace

_ROLE_ZH = {
    "hook": "开场",
    "open": "开场",
    "intro": "开场",
    "body": "主体",
    "demonstration": "展示",
    "demo": "展示",
    "proof": "展示",
    "feature": "展示",
    "detail": "细节",
    "closing": "收尾",
    "close": "收尾",
    "outro": "收尾",
    "ending": "收尾",
    "cta": "收尾",
}

_FRAMING_ZH = {
    "extreme close-up": "特写",
    "extreme_close_up": "特写",
    "close-up": "近景",
    "close_up": "近景",
    "close": "近景",
    "medium close-up": "中近景",
    "medium_close_up": "中近景",
    "medium": "中景",
    "wide": "远景",
    "full": "全景",
}

_MOTION_ZH = {
    "static": "固定",
    "locked": "固定",
    "handheld": "手持",
    "pan": "摇摄",
    "tilt": "俯仰移动",
    "push": "推近",
    "push-in": "推近",
    "push_in": "推近",
    "pull": "拉远",
    "pull-out": "拉远",
    "pull_out": "拉远",
    "tracking": "跟拍",
    "track": "跟拍",
}


def _format_time(value: MediaTime | None, *, zh: bool) -> str:
    if value is None:
        return "-"
    seconds = Fraction(value.value, value.scale)
    number = (
        str(seconds.numerator)
        if seconds.denominator == 1
        else f"{float(seconds):.2f}".rstrip("0").rstrip(".")
    )
    return f"{number} 秒" if zh else f"{number} s"


def _role_label(value: str, *, zh: bool, ordinal: int) -> str:
    if not zh:
        return value
    return _ROLE_ZH.get(value.casefold(), f"段落 {ordinal}")


def _framing_label(value: str | None, *, zh: bool) -> str:
    if value is None:
        return "-"
    return _FRAMING_ZH.get(value.casefold(), value) if zh else value


def _motion_label(value: str | None, *, zh: bool) -> str:
    if value is None:
        return "-"
    return _MOTION_ZH.get(value.casefold(), value) if zh else value


def planning_presentation(result: PlanningProductResult, language: str = "en") -> str:
    zh = language == "zh-CN"
    if result.script_plan_ref is None or result.shooting_plan_ref is None:
        if zh:
            return f"拍摄规划未完成：{result.diagnostic or '没有通过复审的方案'}"
        return f"Planning {result.outcome.value}: {result.diagnostic or 'no accepted plans'}"
    workspace = ProjectWorkspace.open(result.project_location)
    script = workspace.scripts.load(result.script_plan_ref)
    shooting = workspace.shooting_plans.load(result.shooting_plan_ref)
    lines = [
        f"{'脚本方案' if zh else 'ScriptPlan'} {script.envelope.id}@{script.envelope.revision}"
    ]
    for ordinal, section in enumerate(script.sections, start=1):
        role = _role_label(section.narrative_role, zh=zh, ordinal=ordinal)
        lines.extend(
            (
                f"[{role}] {section.information_goal}",
                f"  {'口播' if zh else 'Spoken'}: {section.spoken_content or '-'}",
                f"  {'画面' if zh else 'Visual'}: {section.visual_requirement or '-'}",
                f"  {'时长' if zh else 'Timing'}: {_format_time(section.target_duration, zh=zh)}",
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
    for ordinal, item in enumerate(shooting.requirements, start=1):
        shot_label = f"镜头 {ordinal}" if zh else item.requirement_id
        lines.extend(
            (
                f"[{shot_label}] {item.purpose}",
                f"  {'拍摄' if zh else 'Capture'}: {item.capture_instruction or '-'}",
                f"  {'构图/运动' if zh else 'Framing/motion'}: "
                f"{_framing_label(item.framing, zh=zh)} / "
                f"{_motion_label(item.camera_motion, zh=zh)}",
                f"  {'建议时长' if zh else 'Target duration'}: "
                f"{_format_time(item.target_duration, zh=zh)}",
                f"  {'资源' if zh else 'Resources'}: {item.location_ref or '-'}",
            )
        )
        if item.alternate_coverage:
            lines.append(
                ("  备选拍法: " if zh else "  Alternate coverage: ")
                + "；".join(item.alternate_coverage)
            )
    if shooting.notes:
        separator = "；" if zh else "; "
        lines.append(("备注：" if zh else "Notes: ") + separator.join(shooting.notes))
    return "\n".join(lines)


def editing_presentation(result: EditingProductResult, language: str = "en") -> str:
    zh = language == "zh-CN"
    if result.output_path is not None:
        return (
            f"{'已完成' if zh else 'Completed'}\n"
            f"{'最终视频' if zh else 'Final MP4'}: {result.output_path}"
        )
    if result.review_verdict is not None:
        if zh:
            return "成片检查需要进一步修正。"
        return (
            f"Review: {result.review_verdict.disposition.value}\n"
            f"Correction: {result.review_verdict.correction_route.value}"
        )
    if zh:
        return "自动剪辑未生成可交付输出。"
    return f"Editing {result.outcome.value}: {result.diagnostic or 'no output'}"
