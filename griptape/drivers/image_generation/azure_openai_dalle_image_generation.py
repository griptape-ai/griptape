from __future__ import annotations
import openai
from typing import Optional
from attr import field, Factory, define
from griptape.drivers import OpenAiDalleImageGenerationDriver


@define
class AzureOpenAiDalleImageGenerationDriver(OpenAiDalleImageGenerationDriver):
    """Driver for Azure-hosted OpenAI DALLE image generation API.

    Attributes:
        azure_deployment: An Azure OpenAi deployment id.
        azure_endpoint: An Azure OpenAi endpoint.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_version: An Azure OpenAi API version.
        client: An `openai.AzureOpenAI` client.
    """

    azure_deployment: str = field(kw_only=True)
    azure_endpoint: str = field(kw_only=True)
    azure_ad_token: str | None = field(kw_only=True, default=None)
    azure_ad_token_provider: str | None = field(kw_only=True, default=None)
    api_version: str = field(default="2023-12-01-preview", kw_only=True)
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
