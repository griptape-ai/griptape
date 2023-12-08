from __future__ import annotations

import os
from os import path

from attrs import define, field
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import ImageGenerationEngine
from griptape.loaders.image_loader import ImageLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class ImageGenerator(BaseTool):
    """ImageGenerator is a tool that can be used to generate an image.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    output_dir: str | None = field(default=None, kw_only=True)
    output_file: str | None = field(default=None, kw_only=True)

    @output_dir.validator
    def validate_output_dir(self, _, output_dir: str) -> None:
        if not output_dir:
            return

        if self.output_file:
            raise ValueError("Can't have both output_dir and output_file specified.")

    @output_file.validator
    def validate_output_file(self, _, output_file: str) -> None:
        if not output_file:
            return

        if self.output_dir:
            raise ValueError("Can't have both output_dir and output_file specified.")

    @activity(
        config={
            "description": "Can be used to generate an image from text prompts.",
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
                }
            ),
        }
    )
    def text_to_image(self, params: dict) -> ImageArtifact | ErrorArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]

        image_artifact = self.image_generation_engine.text_to_image(prompts=prompts, negative_prompts=negative_prompts)

        if self.output_dir or self.output_file:
            self._write_to_file(image_artifact)

        return image_artifact

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
    def image_variation(self, params: dict) -> ImageArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]
        image_file = params["values"]["image_file"]

        input_artifact = ImageLoader().load(image_file)

        output_artifact = self.image_generation_engine.image_variation(
            prompts=prompts, negative_prompts=negative_prompts, image=input_artifact
        )

        return output_artifact

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
    def image_inpainting(self, params: dict) -> ImageArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]
        image_file = params["values"]["image_file"]
        mask_file = params["values"]["mask_file"]

        input_artifact = ImageLoader().load(image_file)
        mask_artifact = ImageLoader().load(mask_file)

        output_artifact = self.image_generation_engine.image_inpainting(
            prompts=prompts, negative_prompts=negative_prompts, image=input_artifact, mask=mask_artifact
        )

        return output_artifact

    @activity(
        config={
            "description": "Can be used to modify an input image exclusive of a a specified mask area.",
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
                        description="The path to an image file to used as a base to generate variations from.",
                    ): str,
                    Literal("mask_file", description="The path to mask image file excluding the area to modify."): str,
                }
            ),
        }
    )
    def image_outpainting(self, params: dict) -> ImageArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]
        image_file = params["values"]["image_file"]
        mask_file = params["values"]["mask_file"]

        input_artifact = ImageLoader().load(image_file)
        mask_artifact = ImageLoader().load(mask_file)

        output_artifact = self.image_generation_engine.image_outpainting(
            prompts=prompts, negative_prompts=negative_prompts, image=input_artifact, mask=mask_artifact
        )

        return output_artifact

    def _write_to_file(self, image_artifact: ImageArtifact) -> None:
        if self.output_file:
            outfile = self.output_file
        else:
            outfile = path.join(self.output_dir, image_artifact.name)

        if path.dirname(outfile):
            os.makedirs(path.dirname(outfile), exist_ok=True)

        with open(outfile, "wb") as f:
            f.write(image_artifact.value)
