from attr import field, define
from griptape.drivers import BaseEmbeddingDriver


@define
class MockEmbeddingDriver(BaseEmbeddingDriver):
    dimensions: int = field(default=42, kw_only=True)
    max_attempts: int = field(default=1, kw_only=True)

    def try_embed_string(self, string: str) -> list[float]:
        return [0, 1]
