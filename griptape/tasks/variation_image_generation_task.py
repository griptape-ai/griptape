from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.engines import VariationImageGenerationEngine
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.tasks import BaseImageGenerationTask, BaseTask
from griptape.utils import J2


@define
class VariationImageGenerationTask(BaseImageGenerationTask):
    """A task that generates a variation of an image using a prompt. Accepts a text prompt and image as
    input in one of the following formats:
    - tuple of (template string, ImageArtifact)
    - tuple of (TextArtifact, ImageArtifact)
    - Callable that returns a tuple of (TextArtifact, ImageArtifact)

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    _image_generation_engine: VariationImageGenerationEngine = field(
        default=None, kw_only=True, alias="image_generation_engine"
    )
    _input: tuple[str | TextArtifact, ImageArtifact] | Callable[[BaseTask], tuple[TextArtifact, ImageArtifact]] = field(
        default=None
    )

    @property
    def input(self) -> tuple[TextArtifact, ImageArtifact]:
        if isinstance(self._input, tuple):
            if isinstance(self._input[0], TextArtifact):
                input_text = self._input[0]
            else:
                input_text = TextArtifact(J2().render_from_string(self._input[0], **self.full_context))

            return input_text, self._input[1]
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError("Input must be a tuple of (text, image) or a callable that returns such a tuple.")

    @input.setter
    def input(self, value: tuple[TextArtifact, ImageArtifact]) -> None:
        self._input = value

    @property
    def image_generation_engine(self) -> VariationImageGenerationEngine:
        if self._image_generation_engine is None:
            if self.structure is not None:
                self._image_generation_engine = VariationImageGenerationEngine(
                    image_generation_driver=self.structure.config.global_drivers.image_generation_driver
                )
            else:
                raise ValueError("Image Generation Engine is not set.")
        return self._image_generation_engine

    @image_generation_engine.setter
    def image_generation_engine(self, value: VariationImageGenerationEngine) -> None:
        self._image_generation_engine = value

    def run(self) -> ImageArtifact:
        prompt_artifact = self.input[0]
        image_artifact = self.input[1]

        output_image_artifact = self.image_generation_engine.run(
            prompts=[prompt_artifact.to_text()],
            image=image_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_image_artifact)

        return output_image_artifact
