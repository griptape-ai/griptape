from __future__ import annotations

from typing import Callable, Optional

from attrs import define, field

from griptape.drivers import BaseEmbeddingDriver
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(default="foo", kw_only=True)
    dimensions: int = field(default=42, kw_only=True)
    max_attempts: int = field(default=1, kw_only=True)
    tokenizer: MockTokenizer = field(factory=lambda: MockTokenizer(model="foo bar"), kw_only=True)
    mock_output_function: Callable[[str], Optional[list[float]]] = field(default=lambda chunk: None, kw_only=None)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        output = self.mock_output_function(chunk)
        if output is None:
            return [0, 1]
        else:
            return output
