from __future__ import annotations

from typing import Optional

from attrs import define

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver


@define
class MockImageQueryDriver(BaseImageQueryDriver):
    model: Optional[str] = None

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        return TextArtifact(value="mock text")
