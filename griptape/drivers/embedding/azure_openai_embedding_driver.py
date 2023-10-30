from __future__ import annotations

from attr import define, field, Factory
from griptape.drivers import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer


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

    model: str = field(kw_only=True)
    deployment_id: str = field(kw_only=True)
    api_base: str = field(kw_only=True)
    api_type: str = field(default="azure", kw_only=True)
    api_version: str = field(default="2023-05-15", kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(
            lambda self: OpenAiTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )

    def _params(self, chunk: list[int] | str) -> dict:
        return super()._params(chunk) | {"deployment_id": self.deployment_id}
