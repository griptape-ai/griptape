from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import NopException


class NopEmbeddingDriver(BaseEmbeddingDriver):
    def try_embed_chunk(self, chunk: str) -> list[float]:
        raise NopException(__class__.__name__, "try_embed_chunk")
