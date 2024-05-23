from typing import Optional
from attrs import define, field
from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import DummyException


@define
class DummyEmbeddingDriver(BaseEmbeddingDriver):
    model: Optional[str] = field(init=False)

    def __attrs_post_init__(self):
        self.model = None

    def try_embed_chunk(self, chunk: str) -> list[float]:
        raise DummyException(__class__.__name__, "try_embed_chunk")
