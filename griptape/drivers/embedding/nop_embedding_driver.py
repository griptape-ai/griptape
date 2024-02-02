from attrs import define, field
from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import NopException


@define
class NopEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(init=False)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        raise NopException(__class__.__name__, "try_embed_chunk")
