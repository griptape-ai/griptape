from griptape.drivers import BaseEmbeddingDriver


class MockEmbeddingDriver(BaseEmbeddingDriver):
    def try_embed_string(self, string: str) -> list[float]:
        return [0, 1]
