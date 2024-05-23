from attrs import define, field
from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import DummyException


@define
class DummyEmbeddingDriver(BaseEmbeddingDriver):
    model: None = field(init=False, default=None, kw_only=True)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        raise DummyException(__class__.__name__, "try_embed_chunk")
