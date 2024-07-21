from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.engines import OutpaintingImageGenerationEngine
from griptape.tasks import BaseImageGenerationTask, BaseTask
from griptape.utils import J2


@define
class OutpaintingImageGenerationTask(BaseImageGenerationTask):
    """A task that modifies an image outside the bounds of a mask.

    Accepts a text prompt, image, and mask as
    input in one of the following formats:
    - tuple of (template string, ImageArtifact, ImageArtifact)
    - tuple of (TextArtifact, ImageArtifact, ImageArtifact)
    - Callable that returns a tuple of (TextArtifact, ImageArtifact, ImageArtifact).

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    _image_generation_engine: OutpaintingImageGenerationEngine = field(
        default=None,
        kw_only=True,
        alias="image_generation_engine",
    )
    _input: (
        tuple[str | TextArtifact, ImageArtifact, ImageArtifact] | Callable[[BaseTask], ListArtifact] | ListArtifact
    ) = field(default=None)

    @property
    def input(self) -> ListArtifact:
        if isinstance(self._input, ListArtifact):
            return self._input
        elif isinstance(self._input, tuple):
            if isinstance(self._input[0], TextArtifact):
                input_text = self._input[0]
            else:
                input_text = TextArtifact(J2().render_from_string(self._input[0], **self.full_context))

            return ListArtifact([input_text, self._input[1], self._input[2]])
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be a tuple of (text, image, mask) or a callable that returns such a tuple.")

    @input.setter
    def input(
        self,
        value: tuple[str | TextArtifact, ImageArtifact, ImageArtifact] | Callable[[BaseTask], ListArtifact],
    ) -> None:
        self._input = value

    @property
    def image_generation_engine(self) -> OutpaintingImageGenerationEngine:
        if self._image_generation_engine is None:
            if self.structure is not None:
                self._image_generation_engine = OutpaintingImageGenerationEngine(
                    image_generation_driver=self.structure.config.image_generation_driver,
                )
            else:
                raise ValueError("Image Generation Engine is not set.")

        return self._image_generation_engine

    @image_generation_engine.setter
    def image_generation_engine(self, value: OutpaintingImageGenerationEngine) -> None:
        self._image_generation_engine = value

    def run(self) -> ImageArtifact:
        prompt_artifact = self.input[0]

        image_artifact = self.input[1]
        if not isinstance(image_artifact, ImageArtifact):
            raise ValueError("Image must be an ImageArtifact.")

        mask_artifact = self.input[2]
        if not isinstance(mask_artifact, ImageArtifact):
            raise ValueError("Mask must be an ImageArtifact.")

        output_image_artifact = self.image_generation_engine.run(
            prompts=[prompt_artifact.to_text()],
            image=image_artifact,
            mask=mask_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_image_artifact)

        return output_image_artifact
