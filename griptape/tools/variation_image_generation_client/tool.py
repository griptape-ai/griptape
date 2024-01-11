from __future__ import annotations

from typing import Any

from attrs import define, field
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import VariationImageGenerationEngine
from griptape.loaders import ImageLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.mixins import ImageArtifactFileOutputMixin


@define
class VariationImageGenerationClient(ImageArtifactFileOutputMixin, BaseTool):
    """A tool that can be used to generate prompted variations of an image.

    Attributes:
        engine: The variation image generation engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    engine: VariationImageGenerationEngine = field(kw_only=True)
    image_loader: ImageLoader = field(default=ImageLoader(), kw_only=True)

    @activity(
        config={
            "description": "Can be used to generate a variation of a given input image.",
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
                }
            ),
        }
    )
    def image_variation(self, params: dict[str, Any]) -> ImageArtifact | ErrorArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]
        image_file = params["values"]["image_file"]

        input_artifact = self.image_loader.load(image_file)
        if isinstance(input_artifact, ErrorArtifact):
            return input_artifact

        output_artifact = self.engine.run(prompts=prompts, negative_prompts=negative_prompts, image=input_artifact)

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
