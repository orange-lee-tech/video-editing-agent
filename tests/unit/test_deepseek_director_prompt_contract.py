from video_editing_agent.providers.llm.deepseek_director import _SYSTEM_PROMPT


def test_deepseek_director_prompt_declares_strict_scalar_types() -> None:
    assert "slot_id must be a non-empty string" in _SYSTEM_PROMPT
    assert "order must be a non-negative integer" in _SYSTEM_PROMPT
    assert "allow_reuse must be boolean" in _SYSTEM_PROMPT
    assert "importance must be an integer from 1 through 3" in _SYSTEM_PROMPT
    assert "{value:int,scale:int}" in _SYSTEM_PROMPT
    assert "scale must be a positive integer greater than 0" in _SYSTEM_PROMPT
    assert '"minimum_duration":{"value":1,"scale":2}' in _SYSTEM_PROMPT
    assert "repair_feedback" in _SYSTEM_PROMPT
    assert "Never return Shot IDs, Asset IDs, source timestamps" in _SYSTEM_PROMPT
