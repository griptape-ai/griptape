from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask, BaseTask
from griptape.utils import J2


@define
class ImageOutpaintingTask(BaseImageGenerationTask):
    """A task that modifies an image outside the bounds of a mask.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    _input: tuple[TextArtifact, ImageArtifact, ImageArtifact] | Callable[
        [BaseTask], tuple[TextArtifact, ImageArtifact, ImageArtifact]
    ] = field(default=None, kw_only=True)

    @property
    def input(self) -> (TextArtifact, ImageArtifact, ImageArtifact):
        if (
            isinstance(self._input, tuple)
            and isinstance(self._input[0], TextArtifact)
            and isinstance(self._input[1], ImageArtifact)
            and isinstance(self._input[2], ImageArtifact)
        ):
            return self._input
        if (
            isinstance(self._input, tuple)
            and isinstance(self._input[0], str)
            and isinstance(self._input[1], ImageArtifact)
            and isinstance(self._input[2], ImageArtifact)
        ):
            return (
                TextArtifact(J2().render_from_string(self._input[0], **self.full_context)),
                self._input[1],
                self._input[2],
            )
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
