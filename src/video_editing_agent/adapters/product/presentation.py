from __future__ import annotations

from fractions import Fraction

from video_editing_agent.application.use_cases.product_flow import (
    EditingProductResult,
    PlanningProductResult,
    ProductFlowOutcome,
)
from video_editing_agent.domain.common.media_time import MediaTime
from video_editing_agent.providers.usage import TokenUsageSnapshot
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


def token_usage_presentation(snapshot: TokenUsageSnapshot, language: str = "en") -> str:
    usage = snapshot.usage
    estimated = "≈" if usage.source != "reported" else ""
    if language == "zh-CN":
        details = []
        if usage.cached_input_tokens:
            details.append(f"缓存输入={usage.cached_input_tokens:,}")
        if usage.reasoning_tokens:
            details.append(f"推理={usage.reasoning_tokens:,}")
        suffix = "" if not details else " " + " ".join(details)
        return (
            f"[AI 用量] {usage.provider}/{usage.model} "
            f"输入={estimated}{usage.input_tokens:,} "
            f"输出={estimated}{usage.output_tokens:,} "
            f"合计={estimated}{usage.total_tokens:,}{suffix} "
            f"该提供方累计={snapshot.provider_session_tokens:,} "
            f"本次程序累计={snapshot.process_session_tokens:,}"
        )
    details = []
    if usage.cached_input_tokens:
        details.append(f"cached_in={usage.cached_input_tokens:,}")
    if usage.reasoning_tokens:
        details.append(f"reasoning={usage.reasoning_tokens:,}")
    suffix = "" if not details else " " + " ".join(details)
    return (
        f"[AI usage] {usage.provider}/{usage.model} "
        f"input={estimated}{usage.input_tokens:,} "
        f"output={estimated}{usage.output_tokens:,} "
        f"total={estimated}{usage.total_tokens:,}{suffix} "
        f"provider_session={snapshot.provider_session_tokens:,} "
        f"process_session={snapshot.process_session_tokens:,}"
    )


def _review_correction_summary(result: EditingProductResult, *, zh: bool) -> str:
    assert result.review_verdict is not None
    verdict = result.review_verdict
    route = verdict.correction_route.value
    problems = tuple(finding.problem for finding in verdict.report.findings)
    if zh:
        route_text = {
            "rerender_same_edl": "渲染执行或输出验证失败，系统需要按同一剪辑时间线重新渲染。",
            "return_to_audio_editorial": "音频质量检查未通过，需要重新处理音频后再交付。",
            "escalate_owner": "成片技术检查未通过，需要检查渲染器或运行环境。",
        }.get(route, "成片检查未通过，需要进一步修正。")
        lines = [
            (
                "自动剪辑生成了候选视频，但最终检查未通过。"
                if result.output_path is not None
                else "自动剪辑未生成通过验证的最终视频。"
            ),
            route_text,
        ]
        if problems:
            lines.append("技术详情：" + "；".join(problems))
        if result.output_path is not None:
            lines.append(f"候选视频（未通过最终检查）: {result.output_path}")
        return "\n".join(lines)
    lines = [
        (
            "Editing produced a candidate, but final review did not pass."
            if result.output_path is not None
            else "Editing did not produce a verified final video."
        ),
        f"Correction route: {route}",
    ]
    if problems:
        lines.append("Technical detail: " + "; ".join(problems))
    if result.output_path is not None:
        lines.append(f"Candidate video (not approved): {result.output_path}")
    return "\n".join(lines)


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
    if result.outcome is ProductFlowOutcome.COMPLETED and result.output_path is not None:
        return (
            f"{'已完成' if zh else 'Completed'}\n"
            f"{'最终视频' if zh else 'Final MP4'}: {result.output_path}"
        )
    if result.review_verdict is not None:
        return _review_correction_summary(result, zh=zh)
    if zh:
        detail = result.diagnostic or "没有生成可交付输出"
        return f"自动剪辑失败：{detail}"
    return f"Editing {result.outcome.value}: {result.diagnostic or 'no output'}"
