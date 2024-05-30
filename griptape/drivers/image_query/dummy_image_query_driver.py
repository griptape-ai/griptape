from attrs import define, field

from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.exceptions import DummyException


@define
class DummyImageQueryDriver(BaseImageQueryDriver):
    model: None = field(init=False, default=None, kw_only=True)
    max_tokens: None = field(init=False, default=None, kw_only=True)

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        raise DummyException(__class__.__name__, "try_query")
