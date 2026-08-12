from video_editing_agent.providers.llm import deepseek_chat


def test_script_generation_prompt_separates_editorial_framing_from_product_facts() -> None:
    prompt = deepseek_chat._SCRIPT_SYSTEM_PROMPT

    assert "objective, audience, and core_message may guide editorial framing" in prompt
    assert "Concrete product claims must be directly supported by authoritative_facts" in prompt
    assert "capacity is enough for a use case" in prompt
    assert "fits easily in a bag" in prompt
    assert "one-hand operation or leak resistance" in prompt


def test_shooting_generation_prompt_requires_semantic_location_identity() -> None:
    prompt = deepseek_chat._SHOOTING_SYSTEM_PROMPT

    assert "natural-language location cue" in prompt
    assert "semantically compatible with the referenced location's label and notes" in prompt
    assert "valid location_ref does not authorize a different place" in prompt
    assert "entryway reference must not be described as a sink location" in prompt
    assert "not directly supported by authoritative_facts or the clean ScriptPlan" in prompt


def test_generation_keeps_non_thinking_default_after_reviewer_hardening() -> None:
    assert deepseek_chat.DeepSeekChatConfig().thinking_enabled is False
