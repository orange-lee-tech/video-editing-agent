from __future__ import annotations

import os
from dataclasses import dataclass

from video_editing_agent.application.ports.director import DirectorPort
from video_editing_agent.application.ports.preproduction_planning import (
    ScriptPlanningPort,
    ShootingPlanningPort,
)
from video_editing_agent.application.ports.preproduction_review import (
    ScriptProposalReviewPort,
    ShootingProposalReviewPort,
)
from video_editing_agent.providers.llm.deepseek_chat import (
    PLANNING_TEMPERATURE,
    DeepSeekChatConfig,
    DeepSeekChatTransport,
    DeepSeekScriptPlanningPort,
    DeepSeekShootingPlanningPort,
    UrllibDeepSeekChatTransport,
)
from video_editing_agent.providers.llm.deepseek_director import DeepSeekDirectorPort
from video_editing_agent.providers.llm.deepseek_preproduction_review import (
    REVIEW_INITIAL_MAX_TOKENS,
    DeepSeekScriptProposalReviewPort,
    DeepSeekShootingProposalReviewPort,
)
from video_editing_agent.providers.llm.preproduction_refinement import (
    EditoriallyRefinedScriptPlanningPort,
    EditoriallyRefinedShootingPlanningPort,
)
from video_editing_agent.providers.usage import MeteredDeepSeekChatTransport


class ProviderConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PreproductionPorts:
    script_planning: ScriptPlanningPort
    script_review: ScriptProposalReviewPort
    shooting_planning: ShootingPlanningPort
    shooting_review: ShootingProposalReviewPort


def deepseek_preproduction_ports(
    *,
    model: str = "deepseek-v4-flash",
    transport: DeepSeekChatTransport | None = None,
    output_language: str | None = None,
) -> PreproductionPorts:
    if transport is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key.strip():
            raise ProviderConfigurationError("DEEPSEEK_API_KEY is required for provider=deepseek")
        transport = MeteredDeepSeekChatTransport(UrllibDeepSeekChatTransport(api_key=api_key))
    generation = DeepSeekChatConfig(
        model=model,
        thinking_enabled=False,
        max_tokens=6_000,
        temperature=PLANNING_TEMPERATURE,
    )
    review = DeepSeekChatConfig(
        model=model,
        thinking_enabled=True,
        max_tokens=REVIEW_INITIAL_MAX_TOKENS,
        temperature=None,
    )
    script_generation = DeepSeekScriptPlanningPort(transport=transport, config=generation)
    shooting_generation = DeepSeekShootingPlanningPort(transport=transport, config=generation)
    return PreproductionPorts(
        EditoriallyRefinedScriptPlanningPort(
            script_generation,
            output_language=output_language,
        ),
        DeepSeekScriptProposalReviewPort(transport=transport, config=review),
        EditoriallyRefinedShootingPlanningPort(
            shooting_generation,
            output_language=output_language,
        ),
        DeepSeekShootingProposalReviewPort(transport=transport, config=review),
    )


def deepseek_director_port(
    *, model: str = "deepseek-v4-flash", transport: DeepSeekChatTransport | None = None
) -> DirectorPort:
    if transport is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key.strip():
            raise ProviderConfigurationError("DEEPSEEK_API_KEY is required for provider=deepseek")
        transport = MeteredDeepSeekChatTransport(UrllibDeepSeekChatTransport(api_key=api_key))
    return DeepSeekDirectorPort(
        transport=transport,
        config=DeepSeekChatConfig(
            model=model,
            thinking_enabled=False,
            max_tokens=4_000,
            temperature=PLANNING_TEMPERATURE,
        ),
    )
