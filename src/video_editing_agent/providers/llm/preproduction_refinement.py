from __future__ import annotations

import json
from dataclasses import replace

from video_editing_agent.application.ports.preproduction_planning import (
    NarrativeSectionProposal,
    ScriptPlanningPort,
    ScriptPlanningRequest,
    ScriptPlanProposal,
    ShootingPlanningPort,
    ShootingPlanningRequest,
    ShootingPlanProposal,
    ShotRequirementProposal,
)
from video_editing_agent.domain.brief.model import Brief
from video_editing_agent.domain.common.media_time import MediaTime

_SUPPORTED_OUTPUT_LANGUAGES = frozenset({"zh-CN", "en"})


def _target_language(brief: Brief) -> str:
    """Infer a fallback language when a non-GUI caller did not provide one explicitly."""

    text = " ".join(
        value
        for value in (
            brief.title,
            brief.objective,
            brief.audience,
            brief.platform,
            brief.core_message,
            brief.product_topic or "",
            brief.user_notes or "",
            *(fact.statement for fact in brief.authoritative_facts),
        )
        if value
    )
    cjk = sum("\u3400" <= char <= "\u9fff" for char in text)
    latin = sum(char.isascii() and char.isalpha() for char in text)
    return "zh-CN" if cjk >= latin else "en"


def _resolved_language(explicit: str | None, brief: Brief) -> str:
    if explicit is None:
        return _target_language(brief)
    if explicit not in _SUPPORTED_OUTPUT_LANGUAGES:
        raise ValueError(f"unsupported planning output language: {explicit}")
    return explicit


def _language_rule(language: str) -> str:
    if language == "zh-CN":
        return (
            "输出语言硬约束：所有面向普通用户的自然语言字段必须使用简体中文。"
            "ID、枚举值和事实 ID 可以保持机器格式。若权威事实原文不是中文，可以忠实翻译，"
            "但不得增加、删减或强化事实含义，并保留数字和单位。"
        )
    return (
        "Output-language hard rule: every ordinary-user natural-language field must be in English. "
        "IDs, enum values, and fact IDs may remain machine-formatted. If an authoritative fact is "
        "written in another language, translate it faithfully without adding, removing, or "
        "strengthening meaning, and preserve numbers and units."
    )


def _merge_instruction(original: str | None, extra: str) -> str:
    if original is None:
        return extra
    return f"{original}\n\n{extra}"


def _time_payload(value: MediaTime | None) -> dict[str, int] | None:
    if value is None:
        return None
    return {"value": value.value, "scale": value.scale}


def _script_section_payload(section: NarrativeSectionProposal) -> dict[str, object]:
    return {
        "section_id": section.section_id,
        "narrative_role": section.narrative_role,
        "information_goal": section.information_goal,
        "spoken_content": section.spoken_content,
        "visual_requirement": section.visual_requirement,
        "target_duration": _time_payload(section.target_duration),
        "on_screen_text_intent": section.on_screen_text_intent,
        "emotion": section.emotion,
        "pacing": section.pacing,
        "music_intent": section.music_intent,
        "editing_intent": section.editing_intent,
        "importance": section.importance,
        "protected_fact_ids": list(section.protected_fact_ids),
        "locked": section.locked,
    }


def _script_payload(proposal: ScriptPlanProposal) -> dict[str, object]:
    return {"sections": [_script_section_payload(section) for section in proposal.sections]}


def _shooting_requirement_payload(requirement: ShotRequirementProposal) -> dict[str, object]:
    return {
        "requirement_id": requirement.requirement_id,
        "script_section_ref": requirement.script_section_ref,
        "purpose": requirement.purpose,
        "subject": requirement.subject,
        "action": requirement.action,
        "location_ref": requirement.location_ref,
        "environment_description": requirement.environment_description,
        "framing": requirement.framing,
        "camera_motion": requirement.camera_motion,
        "target_duration": _time_payload(requirement.target_duration),
        "minimum_duration": _time_payload(requirement.minimum_duration),
        "audio_dialogue_requirement": requirement.audio_dialogue_requirement,
        "continuity_hint": requirement.continuity_hint,
        "visual_constraints": list(requirement.visual_constraints),
        "priority": requirement.priority,
        "backup_intent": requirement.backup_intent,
        "capture_instruction": requirement.capture_instruction,
        "alternate_coverage": list(requirement.alternate_coverage),
        "handle_before": _time_payload(requirement.handle_before),
        "handle_after": _time_payload(requirement.handle_after),
    }


def _shooting_payload(proposal: ShootingPlanProposal) -> dict[str, object]:
    return {
        "requirements": [
            _shooting_requirement_payload(requirement) for requirement in proposal.requirements
        ],
        "notes": list(proposal.notes),
    }


def _script_quality_instruction(language: str, draft: ScriptPlanProposal | None = None) -> str:
    rules = (
        f"{_language_rule(language)}\n"
        "Editorial-quality rules: produce a useful short-form commercial script without inventing "
        "product facts. Give Hook, Body/Demonstration, and Closing clearly different narrative "
        "jobs. Do not mechanically repeat the same authoritative fact in spoken content or "
        "on-screen text across multiple sections unless the user explicitly requested repetition. "
        "A Hook may use a claim-free question, situation, or visual reveal. A Body/Demonstration "
        "should carry the strongest verified information once and pair it with observable product "
        "coverage. A Closing should finish the story or use a claim-free call to action rather "
        "than restating the same fact. Lifestyle framing, pacing, shot variety, curiosity, and "
        "calls to learn more are creative devices, not authority for new product properties. Keep "
        "the result concise but genuinely useful; factual safety must not collapse the script into "
        "three paraphrases of one sentence. Preserve locked sections exactly."
    )
    if draft is None:
        return rules
    draft_json = json.dumps(_script_payload(draft), ensure_ascii=False, separators=(",", ":"))
    return (
        f"{rules}\n\nEditorial refinement pass: the JSON below is a draft proposal, not factual "
        "authority. Regenerate one complete ScriptPlan proposal using the same Brief and contract. "
        "Improve repetition, narrative progression, platform usefulness, and natural wording while "
        "preserving every hard constraint and never adding an unsupported claim.\n"
        f"draft_proposal={draft_json}"
    )


def _shooting_quality_instruction(language: str, draft: ShootingPlanProposal | None = None) -> str:
    rules = (
        f"{_language_rule(language)}\n"
        "Shooting-quality rules: write for an ordinary phone user, not a professional crew. Each "
        "required shot should make the setup and action easy to execute: say where/how to place or "
        "hold the phone, what should enter the frame, what action to perform, and when to hold "
        "still. Use practical pre-roll/post-roll handles where useful and provide simple alternate "
        "coverage for important shots. Vary framing or camera movement across the sequence when it "
        "improves clarity, but do not add equipment the user did not declare. Do not require a "
        "physical label, measuring tool, prop, location, or person unless it is declared "
        "available. Verified facts may appear as narration or on-screen text; filming instructions "
        "must not turn them into a stronger unsupported demonstration."
    )
    if draft is None:
        return rules
    draft_json = json.dumps(_shooting_payload(draft), ensure_ascii=False, separators=(",", ":"))
    return (
        f"{rules}\n\nShooting refinement pass: the JSON below is a draft proposal, not authority. "
        "Regenerate one complete ShootingPlan under the same ScriptPlan and ProductionConstraints. "
        "Make the instructions clearer, more concrete, and easier for a beginner to follow without "
        "adding product claims or undeclared resources.\n"
        f"draft_proposal={draft_json}"
    )


class EditoriallyRefinedScriptPlanningPort(ScriptPlanningPort):
    """Spend one extra text-model pass on editorial quality before independent semantic review."""

    def __init__(self, delegate: ScriptPlanningPort, *, output_language: str | None = None) -> None:
        if output_language is not None and output_language not in _SUPPORTED_OUTPUT_LANGUAGES:
            raise ValueError(f"unsupported planning output language: {output_language}")
        self._delegate = delegate
        self._output_language = output_language

    def propose(self, request: ScriptPlanningRequest) -> ScriptPlanProposal:
        language = _resolved_language(self._output_language, request.brief)
        draft = self._delegate.propose(
            replace(
                request,
                instruction=_merge_instruction(
                    request.instruction, _script_quality_instruction(language)
                ),
            )
        )
        return self._delegate.propose(
            replace(
                request,
                instruction=_merge_instruction(
                    request.instruction,
                    _script_quality_instruction(language, draft),
                ),
            )
        )


class EditoriallyRefinedShootingPlanningPort(ShootingPlanningPort):
    """Spend one extra text-model pass on beginner-friendly shooting-plan quality."""

    def __init__(
        self, delegate: ShootingPlanningPort, *, output_language: str | None = None
    ) -> None:
        if output_language is not None and output_language not in _SUPPORTED_OUTPUT_LANGUAGES:
            raise ValueError(f"unsupported planning output language: {output_language}")
        self._delegate = delegate
        self._output_language = output_language

    def propose(self, request: ShootingPlanningRequest) -> ShootingPlanProposal:
        language = _resolved_language(self._output_language, request.brief)
        draft = self._delegate.propose(
            replace(
                request,
                instruction=_merge_instruction(
                    request.instruction, _shooting_quality_instruction(language)
                ),
            )
        )
        return self._delegate.propose(
            replace(
                request,
                instruction=_merge_instruction(
                    request.instruction,
                    _shooting_quality_instruction(language, draft),
                ),
            )
        )
