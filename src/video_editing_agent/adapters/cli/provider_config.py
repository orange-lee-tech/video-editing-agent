from __future__ import annotations

import os
from dataclasses import dataclass

from video_editing_agent.application.ports.preproduction_planning import (
    ScriptPlanningPort,
    ShootingPlanningPort,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReviewPort,
    ShootingProposalReviewPort,
)
from video_editing_agent.providers.llm.deepseek_chat import (
    DeepSeekChatConfig,
    DeepSeekScriptPlanningPort,
    DeepSeekShootingPlanningPort,
    UrllibDeepSeekChatTransport,
)
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    DeepSeekScriptProposalReviewPort,
    DeepSeekShootingProposalReviewPort,
)


class ProviderConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PreproductionPorts:
    script_planning: ScriptPlanningPort
    script_review: ScriptProposalReviewPort
    shooting_planning: ShootingPlanningPort
    shooting_review: ShootingProposalReviewPort


def deepseek_preproduction_ports(*, model: str = "deepseek-v4-flash") -> PreproductionPorts:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key.strip():
        raise ProviderConfigurationError("DEEPSEEK_API_KEY is required for provider=deepseek")
    transport = UrllibDeepSeekChatTransport(api_key=api_key)
    generation = DeepSeekChatConfig(model=model, thinking_enabled=False, max_tokens=6_000)
    review = DeepSeekChatConfig(model=model, thinking_enabled=True, max_tokens=6_000)
    return PreproductionPorts(
        DeepSeekScriptPlanningPort(transport=transport, config=generation),
        DeepSeekScriptProposalReviewPort(transport=transport, config=review),
        DeepSeekShootingPlanningPort(transport=transport, config=generation),
        DeepSeekShootingProposalReviewPort(transport=transport, config=review),
    )
