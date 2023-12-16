from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask, BaseTask


@define
class ImageOutpaintingTask(BaseImageGenerationTask):
    """A task that modifies an image outside the bounds of a mask.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
        image_file: The path to the input image file.
        mask_file: If provided, load this image as a mask for input modifications. Must match the dimensions of
            the input image.
    """

    image_file: str = field(kw_only=True)
    mask_file: str | None = field(default=None, kw_only=True)
    _input: tuple[TextArtifact, ImageArtifact, ImageArtifact] | Callable[
        [BaseTask], tuple[TextArtifact, ImageArtifact, ImageArtifact]
    ] = field(default=None, kw_only=True)

    @property
    def input(self) -> (TextArtifact, ImageArtifact, ImageArtifact):
        if isinstance(self._input, (TextArtifact, ImageArtifact)):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be a tuple of (text, image, mask) or a callable that returns such a tuple.")

    @input.setter
    def input(self, value: (TextArtifact, ImageArtifact, ImageArtifact)) -> None:
        self._input = value

    def run(self) -> ImageArtifact:
        prompt_artifact = self.input[0]
        image_artifact = self.input[1]
        mask_artifact = self.input[2]

        output_image_artifact = self.image_generation_engine.image_outpainting(
            prompts=[prompt_artifact.to_text()],
            image=image_artifact,
            mask=mask_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_image_artifact)

        return output_image_artifact
