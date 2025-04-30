from __future__ import annotations

from typing import get_args

from attrs import define

from griptape.drivers.embedding.base_embedding_driver import VectorOperation
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver


@define
class NvidiaNimEmbeddingDriver(OpenAiEmbeddingDriver):
    """Nvidia Embedding Driver. The API is OpenAI compatible, but requires an extra parameter 'input_type'."""

    def try_embed_chunk(self, chunk: str, *, vector_operation: VectorOperation | None = None, **kwargs) -> list[float]:
        if vector_operation not in get_args(VectorOperation):
            raise ValueError(f"invalid value for vector_operation, must be one of {get_args(VectorOperation)}")

        extra_body = {
            "input_type": "query" if vector_operation == "query" else "passage",
        }

        return self.client.embeddings.create(**self._params(chunk), extra_body=extra_body).data[0].embedding
