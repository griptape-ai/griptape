from typing import Optional
from attr import define, field

from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.exceptions import DummyException


@define
class DummyImageQueryDriver(BaseImageQueryDriver):
    model: Optional[str] = field(init=False)
    max_tokens: Optional[int] = field(init=False)  # pyright: ignore[reportGeneralTypeIssues]

    def __attrs_post_init__(self):
        self.model = None
        self.max_tokens = None

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        raise DummyException(__class__.__name__, "try_query")
