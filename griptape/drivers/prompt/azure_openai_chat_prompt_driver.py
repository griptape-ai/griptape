from attr import define, field, Factory
from griptape.utils import PromptStack
from griptape.drivers import OpenAiChatPromptDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class AzureOpenAiChatPromptDriver(OpenAiChatPromptDriver):
    """
    Attributes:
        api_base: API URL.
        deployment_id: Azure OpenAI deployment ID.
        model: OpenAI model name.
    """
    api_base: str = field(kw_only=True)
    model: str = field(kw_only=True)
    deployment_id: str = field(kw_only=True)
    api_type: str = field(default="azure", kw_only=True)
    api_version: str = field(default="2023-05-15", kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return super()._base_params(prompt_stack) | {
            "deployment_id": self.deployment_id
        }
