from attrs import define, field
from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import DummyException


@define
class DummyEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(init=False)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        raise DummyException(__class__.__name__, "try_embed_chunk")
