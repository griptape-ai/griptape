from attrs import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask


@define
class MockImageGenerationTask(BaseImageGenerationTask):
    _input: TextArtifact = field(default="input")

    @property
    def input(self) -> TextArtifact:
        return self._input

    @input.setter
    def input(self, value: str) -> None:
        self._input = TextArtifact(value)

    def run(self) -> ImageArtifact:
        return ImageArtifact(value=b"image data", format="png", width=512, height=512)
