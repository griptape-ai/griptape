from attr import define, field, Factory
from typing import Optional
from griptape.drivers import OpenAiChatPromptDriver
from griptape.utils.prompt_stack import PromptStack
from griptape.tokenizers import OpenAiTokenizer
import openai


@define
class AzureOpenAiChatPromptDriver(OpenAiChatPromptDriver):
    """
    Attributes:
        azure_deployment: Azure deployment id.
        azure_endpoint: Azure endpoint.
        azure_ad_token: Azure Active Directory token.
        azure_ad_token_provider: Azure Active Directory token provider.
        api_version: API version.
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
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        )
    )
    tokenizer: OpenAiTokenizer = field(
        default=Factory(
            lambda self: OpenAiTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = super()._base_params(prompt_stack)
        # TODO: Add `seed` parameter once Azure supports it.
        del params["seed"]

        return params
