from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.tasks import BaseImageGenerationTask


@define
class MockImageGenerationTask(BaseImageGenerationTask):
    input: str = field(kw_only=True)

    def run(self) -> ImageArtifact:
        return ImageArtifact(value=b"image data", mime_type="image/png", width=512, height=512)
