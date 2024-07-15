from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import openai
from attrs import Factory, define, field

from griptape.drivers import OpenAiChatPromptDriver

if TYPE_CHECKING:
    from griptape.common import PromptStack


@define
class AzureOpenAiChatPromptDriver(OpenAiChatPromptDriver):
    """Azure OpenAi Chat Prompt Driver.

    Attributes:
        azure_deployment: An optional Azure OpenAi deployment id. Defaults to the model name.
        azure_endpoint: An Azure OpenAi endpoint.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_version: An Azure OpenAi API version.
        client: An `openai.AzureOpenAI` client.
    """

    azure_deployment: str = field(
        kw_only=True,
        default=Factory(lambda self: self.model, takes_self=True),
        metadata={"serializable": True},
    )
    azure_endpoint: str = field(kw_only=True, metadata={"serializable": True})
    azure_ad_token: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    azure_ad_token_provider: Optional[Callable[[], str]] = field(
        kw_only=True,
        default=None,
        metadata={"serializable": False},
    )
    api_version: str = field(default="2023-05-15", kw_only=True, metadata={"serializable": True})
    client: openai.AzureOpenAI = field(
        default=Factory(
            lambda self: openai.AzureOpenAI(
                organization=self.organization,
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.azure_deployment,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        ),
    )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = super()._base_params(prompt_stack)
        # TODO: Add `seed` parameter once Azure supports it.
        if "seed" in params:
            del params["seed"]
        # TODO: Add `stream_options` parameter once Azure supports it.
        if "stream_options" in params:
            del params["stream_options"]

        return params
