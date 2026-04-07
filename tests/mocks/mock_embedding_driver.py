from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.drivers.embedding import BaseEmbeddingDriver
from tests.mocks.mock_tokenizer import MockTokenizer

if TYPE_CHECKING:
    from griptape.artifacts.image_artifact import ImageArtifact
    from griptape.artifacts.text_artifact import TextArtifact


@define
class MockEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(default="foo", kw_only=True)
    dimensions: int = field(default=42, kw_only=True)
    max_attempts: int = field(default=1, kw_only=True)
    tokenizer: MockTokenizer = field(factory=lambda: MockTokenizer(model="foo bar"), kw_only=True)
    mock_output: Callable[[str | TextArtifact | ImageArtifact], list[float]] = field(
        default=lambda chunk: [0, 1], kw_only=True
    )

    def try_embed_artifact(self, artifact: TextArtifact | ImageArtifact, **kwargs) -> list[float]:
        return self.mock_output(artifact)

    def try_embed_chunk(self, chunk: str, **kwargs) -> list[float]:
        return self.mock_output(chunk)
