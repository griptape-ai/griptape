from __future__ import annotations

from typing import Any

from attrs import define, field
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import OutpaintingImageGenerationEngine
from griptape.loaders import ImageLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.mixins import ImageArtifactFileOutputMixin


@define
class OutpaintingImageGenerationClient(ImageArtifactFileOutputMixin, BaseTool):
    """A tool that can be used to generate prompted outpaintings of an image.

    Attributes:
        engine: The outpainting image generation engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    engine: OutpaintingImageGenerationEngine = field(kw_only=True)
    image_loader: ImageLoader = field(default=ImageLoader(), kw_only=True)

    @activity(
        config={
            "description": "Can be used to modify an image within a specified mask area.",
            "schema": Schema(
                {
                    Literal(
                        "prompts",
                        description="A detailed list of features and descriptions to include in the generated image.",
                    ): list[str],
                    Literal(
                        "negative_prompts",
                        description="A detailed list of features and descriptions to avoid in the generated image.",
                    ): list[str],
                    Literal(
                        "image_file",
                        description="The path to an image file to be used as a base to generate variations from.",
                    ): str,
                    Literal("mask_file", description="The path to mask image file defining the area to modify."): str,
                }
            ),
        }
    )
    def image_outpainting(self, params: dict[str, Any]) -> ImageArtifact | ErrorArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]
        image_file = params["values"]["image_file"]
        mask_file = params["values"]["mask_file"]

        input_artifact = self.image_loader.load(image_file)
        mask_artifact = self.image_loader.load(mask_file)

        output_artifact = self.engine.run(
            prompts=prompts, negative_prompts=negative_prompts, image=input_artifact, mask=mask_artifact
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
