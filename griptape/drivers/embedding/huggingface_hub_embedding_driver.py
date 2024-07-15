from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from huggingface_hub import InferenceClient


@define
class HuggingFaceHubEmbeddingDriver(BaseEmbeddingDriver):
    """Hugging Face Hub Embedding Driver.

    Attributes:
        api_token: Hugging Face Hub API token.
        model: Hugging Face Hub model name.
        client: Custom `InferenceApi`.
    """

    api_token: str = field(kw_only=True, metadata={"serializable": True})
    client: InferenceClient = field(
        default=Factory(
            lambda self: import_optional_dependency("huggingface_hub").InferenceClient(
                model=self.model,
                token=self.api_token,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        response = self.client.feature_extraction(chunk)

        return response.flatten().tolist()
