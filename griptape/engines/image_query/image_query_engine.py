from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.config import Config

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact, TextArtifact
    from griptape.drivers import BaseImageQueryDriver


@define
class ImageQueryEngine:
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(lambda: Config.drivers.image_query_driver), kw_only=True
    )

    def run(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        return self.image_query_driver.query(query, images)
