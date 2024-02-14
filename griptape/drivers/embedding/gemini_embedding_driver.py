from __future__ import annotations
from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer, GeminiTokenizer
from vertexai.language_models import TextEmbeddingModel
import openai


@define
class GeminiEmbeddingDriver(BaseEmbeddingDriver):
    """
    Attributes:
        model: OpenAI embedding model name. Defaults to `text-embedding-ada-002`.
        base_url: API URL. Defaults to OpenAI's v1 API URL.
        api_key: API key to pass directly. Defaults to `OPENAI_API_KEY` environment variable.
        organization: OpenAI organization. Defaults to 'OPENAI_ORGANIZATION' environment variable.
    """

    DEFAULT_MODEL = "textembedding-gecko"
    GOOGLE_EMBEDDING_MODELS = ["textembedding-gecko", "textembedding-gecko-multilingual"]

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        return self.client.embeddings.create(**self._params(chunk)).data[0].embedding

    def _params(self, chunk: str) -> dict:
        return {"input": chunk, "model": self.model}
