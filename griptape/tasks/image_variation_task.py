from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask, BaseTask


@define
class ImageVariationTask(BaseImageGenerationTask):
    """A task that generates a variation of an image using a prompt.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    _input: tuple[TextArtifact, ImageArtifact] | Callable[[BaseTask], tuple[TextArtifact, ImageArtifact]] = field(
        default=None, kw_only=True
    )

    @property
    def input(self) -> (TextArtifact, ImageArtifact):
        if (
            isinstance(self._input, tuple)
            and isinstance(self._input[0], TextArtifact)
            and isinstance(self._input[1], ImageArtifact)
        ):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be a tuple of (text, image) or a callable that returns such a tuple.")

    @input.setter
    def input(self, value: (TextArtifact, ImageArtifact)) -> None:
        self._input = value

    def run(self) -> ImageArtifact:
        prompt_artifact = self.input[0]
        image_artifact = self.input[1]

        output_image_artifact = self.image_generation_engine.image_variation(
            prompts=[prompt_artifact.to_text()],
            image=image_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_image_artifact)

        return output_image_artifact
