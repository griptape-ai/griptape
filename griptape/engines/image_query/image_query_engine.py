from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver


@define
class ImageQueryEngine:
    image_query_driver: BaseImageQueryDriver = field(kw_only=True)

    def run(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        return self.image_query_driver.query(query, images)
