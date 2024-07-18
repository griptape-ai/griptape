from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.drivers import BaseImageQueryDriver
from griptape.exceptions import DummyError

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact, TextArtifact


@define
class DummyImageQueryDriver(BaseImageQueryDriver):
    model: None = field(init=False, default=None, kw_only=True)
    max_tokens: None = field(init=False, default=None, kw_only=True)

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        raise DummyError(__class__.__name__, "try_query")
