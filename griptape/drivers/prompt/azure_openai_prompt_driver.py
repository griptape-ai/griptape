from attr import define, field, Factory
from griptape.drivers import OpenAiPromptDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class AzureOpenAiPromptDriver(OpenAiPromptDriver):
    api_base: str = field(kw_only=True)
    model: str = field(kw_only=True)
    deployment_id: str = field(kw_only=True)
    api_type: str = field(default="azure", kw_only=True)
    api_version: str = field(default="2023-05-15", kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )

    def _base_params(self, value: str) -> dict:
        return super()._base_params(value) | {
            "deployment_id": self.deployment_id
        }
