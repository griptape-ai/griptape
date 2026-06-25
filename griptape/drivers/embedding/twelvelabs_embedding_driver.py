from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from twelvelabs import TwelveLabs


@define
class TwelveLabsEmbeddingDriver(BaseEmbeddingDriver):
    """TwelveLabs Marengo Embedding Driver.

    Generates multimodal embeddings with TwelveLabs' Marengo model. Marengo maps
    text, images, and video into the same 512-dimensional vector space, so text
    queries can be matched against visual content stored in a vector store.

    Attributes:
        model: TwelveLabs Marengo model name. Defaults to `marengo3.0`.
        api_key: TwelveLabs API key. Defaults to the `TWELVELABS_API_KEY` environment variable.
        client: Optionally provide a custom `twelvelabs.TwelveLabs` client.
    """

    DEFAULT_MODEL = "marengo3.0"

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    _client: TwelveLabs | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> TwelveLabs:
        return import_optional_dependency("twelvelabs").TwelveLabs(api_key=self.api_key)

    def try_embed_artifact(self, artifact: TextArtifact | ImageArtifact, **kwargs) -> list[float]:
        if isinstance(artifact, TextArtifact):
            return self.try_embed_chunk(artifact.value, **kwargs)
        response = self.client.embed.create(
            model_name=self.model,
            image_file=(artifact.name, artifact.value, artifact.mime_type),
        )
        return self._extract_vector(response.image_embedding)

    def try_embed_chunk(self, chunk: str, **kwargs) -> list[float]:
        response = self.client.embed.create(model_name=self.model, text=chunk)
        return self._extract_vector(response.text_embedding)

    def _extract_vector(self, result: Any) -> list[float]:
        if result is None or not result.segments:
            raise ValueError("TwelveLabs returned no embedding segments.")
        vector = result.segments[0].float_
        if vector is None:
            raise ValueError("TwelveLabs returned an empty embedding.")
        return vector
