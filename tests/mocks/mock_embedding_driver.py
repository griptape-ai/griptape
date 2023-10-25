from attr import field, define
from griptape.drivers import BaseEmbeddingDriver
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockEmbeddingDriver(BaseEmbeddingDriver):
    dimensions: int = field(default=42, kw_only=True)
    max_attempts: int = field(default=1, kw_only=True)
    tokenizer: MockTokenizer = field(factory=lambda: MockTokenizer(model="foo bar"), kw_only=True)

    def try_embed_chunk(self, text: str) -> list[float]:
        return [0] * len(text)
