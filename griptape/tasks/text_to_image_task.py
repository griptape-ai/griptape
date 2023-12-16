from __future__ import annotations

from attr import define

from griptape.artifacts import ImageArtifact
from griptape.tasks import BaseImageGenerationTask


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

    def run(self) -> ImageArtifact:
        image_artifact = self.image_generation_engine.text_to_image(
            prompts=[self.input.to_text()], rulesets=self.all_rulesets, negative_rulesets=self.negative_rulesets
        )

        if self.output_dir or self.output_file:
            self._write_to_file(image_artifact)

        return image_artifact
