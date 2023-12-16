from __future__ import annotations

from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.tasks import BaseImageGenerationTask


@define
class ImageInpaintingTask(BaseImageGenerationTask):
    """A task that modifies a select region within an image using a mask.

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

    def run(self) -> ImageArtifact:
        input_image_artifact = self._read_from_file(self.image_file)

        mask_image_artifact = None
        if self.mask_file is not None:
            mask_image_artifact = self._read_from_file(self.mask_file)

        output_image_artifact = self.image_generation_engine.image_inpainting(
            prompts=[self.input.to_text()],
            image=input_image_artifact,
            mask=mask_image_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir is not None or self.output_file is not None:
            self._write_to_file(output_image_artifact)

        return output_image_artifact
