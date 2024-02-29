from typing import Optional
from attr import define
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.drivers.image_generation.base_image_generation_driver import BaseImageGenerationDriver


@define
class MockImageQueryDriver(BaseImageQueryDriver):
    model: Optional[str] = None

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        return TextArtifact(value="mock text")
