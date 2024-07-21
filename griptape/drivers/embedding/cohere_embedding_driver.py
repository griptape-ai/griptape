from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers import CohereTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from cohere import Client


@define
class CohereEmbeddingDriver(BaseEmbeddingDriver):
    """Cohere Embedding Driver.

    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
        tokenizer: Custom `CohereTokenizer`.
        input_type: Cohere embedding input type.
    """

    DEFAULT_MODEL = "models/embedding-001"

    api_key: str = field(kw_only=True, metadata={"serializable": False})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
        kw_only=True,
    )
    tokenizer: CohereTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True,
    )

    input_type: str = field(kw_only=True, metadata={"serializable": True})

    def try_embed_chunk(self, chunk: str) -> list[float]:
        result = self.client.embed(texts=[chunk], model=self.model, input_type=self.input_type)

        if isinstance(result.embeddings, list):
            return result.embeddings[0]
        else:
            raise ValueError("Non-float embeddings are not supported.")
