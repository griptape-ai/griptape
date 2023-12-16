from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask, BaseTask


@define
class TextToImageTask(BaseImageGenerationTask):
    """ImageGenerationTask is a task that can be used to generate an image.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(default=None, kw_only=True)

    @property
    def input(self) -> (TextArtifact, ImageArtifact, ImageArtifact):
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(self._input)

    @input.setter
    def input(self, value: (TextArtifact, ImageArtifact, ImageArtifact)) -> None:
        self._input = value

    def run(self) -> ImageArtifact:
        image_artifact = self.image_generation_engine.text_to_image(
            prompts=[self.input.to_text()], rulesets=self.all_rulesets, negative_rulesets=self.negative_rulesets
        )

        if self.output_dir or self.output_file:
            self._write_to_file(image_artifact)

        return image_artifact
