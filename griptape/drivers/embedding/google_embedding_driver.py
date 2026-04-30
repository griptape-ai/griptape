from __future__ import annotations

from typing import TYPE_CHECKING, cast

from attrs import define, field

from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from google.genai import Client


@define
class GoogleEmbeddingDriver(BaseEmbeddingDriver):
    """Google Embedding Driver.

    Attributes:
        api_key: Google API key.
        model: Google model name.
        client: Custom `google.genai.Client`.
        task_type: Embedding model task type (https://ai.google.dev/gemini-api/docs/embeddings#task-types). Defaults to `retrieval_document`.
        title: Optional title for the content. Only works with `retrieval_document` task type.
    """

    DEFAULT_MODEL = "models/embedding-001"

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    task_type: str = field(default="retrieval_document", kw_only=True, metadata={"serializable": True})
    title: str | None = field(default=None, kw_only=True, metadata={"serializable": True})
    _client: Client | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Client:
        genai = import_optional_dependency("google.genai")

        return genai.Client(api_key=self.api_key)

    def try_embed_chunk(self, chunk: str, **kwargs) -> list[float]:
        types = import_optional_dependency("google.genai.types")

        response = self.client.models.embed_content(
            model=self.model,
            contents=chunk,
            config=types.EmbedContentConfig(task_type=self.task_type, title=self.title),
        )

        return cast("list[float]", response.embeddings[0].values)  # pyright: ignore[reportOptionalSubscript]

    def _params(self, chunk: str) -> dict:
        return {"input": chunk, "model": self.model}
