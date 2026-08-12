from video_editing_agent.planning.authority.commercial import COMMERCIAL_AUTHORITY_SYSTEM_RULES
from video_editing_agent.providers.llm import deepseek_chat


def test_script_generation_prompt_uses_shared_commercial_authority_contract() -> None:
    prompt = deepseek_chat._SCRIPT_SYSTEM_PROMPT

    assert COMMERCIAL_AUTHORITY_SYSTEM_RULES in prompt
    assert "positioning_intent" in prompt
    assert "Concrete product claims" in prompt
    assert "500 mL does not prove" in prompt
    assert "fits easily in a backpack" in prompt
    assert "one-hand operation or leak resistance" in prompt


def test_shooting_generation_prompt_requires_semantic_location_and_claim_authority() -> None:
    prompt = deepseek_chat._SHOOTING_SYSTEM_PROMPT

    assert COMMERCIAL_AUTHORITY_SYSTEM_RULES in prompt
    assert "natural-language location cue" in prompt
    assert "semantically compatible with the referenced location's label and notes" in prompt
    assert "valid location_ref does not authorize a different place" in prompt
    assert "entryway reference must not be described as a sink location" in prompt
    assert "planned successful visual demonstration" in prompt
    assert "fit or adequacy" in prompt


def test_generation_keeps_non_thinking_default_after_reviewer_hardening() -> None:
    assert deepseek_chat.DeepSeekChatConfig().thinking_enabled is False
