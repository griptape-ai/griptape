from typing import Optional
from attr import define, field, Factory
from griptape.drivers import OpenAiCompletionPromptDriver
import openai


@define
class AzureOpenAiCompletionPromptDriver(OpenAiCompletionPromptDriver):
    """
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
    azure_ad_token: Optional[str] = field(kw_only=True, default=None)
    azure_ad_token_provider: Optional[str] = field(kw_only=True, default=None)
    api_version: str = field(default="2023-05-15", kw_only=True)
    client: openai.AzureOpenAI = field(
        default=Factory(
            lambda self: openai.AzureOpenAI(
                organization=self.organization,
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint,
                azure_deployment=self.azure_deployment,
            ),
            takes_self=True,
        )
    )
