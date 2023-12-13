from __future__ import annotations

from typing import Optional
from attr import define, field, Factory
from griptape.drivers import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer
import openai


@define
class AzureOpenAiEmbeddingDriver(OpenAiEmbeddingDriver):
    """
    Attributes:
        azure_deployment: An Azure OpenAi deployment id.
        azure_endpoint: An Azure OpenAi endpoint.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_version: An Azure OpenAi API version.
        tokenizer: An `OpenAiTokenizer`.
        client: An `openai.AzureOpenAI` client.
    """

    azure_deployment: str = field(kw_only=True)
    azure_endpoint: str = field(kw_only=True)
    azure_ad_token: str | None = field(kw_only=True, default=None)
    azure_ad_token_provider: str | None = field(kw_only=True, default=None)
    api_version: str = field(default="2023-05-15", kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
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
        )
    )
