from __future__ import annotations

from attr import define, field, Factory
from griptape.drivers import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer
import openai


@define
class AzureOpenAiEmbeddingDriver(OpenAiEmbeddingDriver):
    """
    Attributes:
        model: OpenAI embedding model name.
        deployment_id: Azure OpenAI deployment ID.
        api_base: API URL.
        api_type: OpenAI API type. Defaults to 'azure'.
        api_version: API version. Defaults to '2023-05-15'.
        tokenizer: Optionally provide custom `OpenAiTokenizer`.
    """

    deployment_id: str = field(kw_only=True)
    api_base: str = field(kw_only=True)
    api_type: str = field(default="azure", kw_only=True)
    api_version: str = field(default="2023-05-15", kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    client: openai.AzureOpenAI = field(
        init=False,
        default=Factory(
            lambda self: openai.AzureOpenAI(
                api_key=self.api_key, base_url=self.base_url, organization=self.organization
            ),
            takes_self=True,
        ),
    )

    def _params(self, chunk: str) -> dict:
        return super()._params(chunk) | {"deployment_id": self.deployment_id}
