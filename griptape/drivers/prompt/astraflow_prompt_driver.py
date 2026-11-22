from __future__ import annotations

from attrs import define, field

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver


@define
class AstraflowPromptDriver(OpenAiChatPromptDriver):
    """Prompt Driver for Astraflow (UCloud / 优刻得).

    Astraflow is an OpenAI-compatible AI model aggregation platform supporting 200+ models.
    Set ``base_url`` to ``https://api.modelverse.cn/v1`` and use ``ASTRAFLOW_CN_API_KEY``
    to use the China endpoint instead of the global endpoint.
    """

    base_url: str = field(default="https://api-us-ca.umodelverse.ai/v1", kw_only=True, metadata={"serializable": True})
