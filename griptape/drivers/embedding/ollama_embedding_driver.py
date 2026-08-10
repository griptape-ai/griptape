from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from ollama import Client


@define
class OllamaEmbeddingDriver(BaseEmbeddingDriver):
    """Ollama Embedding Driver.

    Attributes:
        model: Ollama embedding model name.
        host: Optional Ollama host.
        client: Ollama `Client`.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    host: str | None = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    headers: dict[str, str] | None = field(default=None, kw_only=True, metadata={"serializable": False})
    _client: Client | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Client:
        client_kwargs: dict = {"host": self.host}
        if self.headers is not None:
            client_kwargs["headers"] = self.headers
        if self.api_key is not None:
            client_kwargs["api_key"] = self.api_key
        return import_optional_dependency("ollama").Client(**client_kwargs)

    def try_embed_chunk(self, chunk: str, **kwargs) -> list[float]:
        return list(self.client.embeddings(model=self.model, prompt=chunk)["embedding"])
