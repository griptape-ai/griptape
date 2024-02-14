from __future__ import annotations
from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver
from vertexai.language_models import TextEmbeddingModel


@define
class GeminiEmbeddingDriver(BaseEmbeddingDriver):
    DEFAULT_MODEL = "textembedding-gecko"
    GOOGLE_EMBEDDING_MODELS = ["textembedding-gecko", "textembedding-gecko-multilingual"]

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: TextEmbeddingModel = field(
        default=Factory(
            lambda self: TextEmbeddingModel.from_pretrained(self.model),
            takes_self=True,
        )
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        return self.client.get_embeddings([chunk])[0].values
