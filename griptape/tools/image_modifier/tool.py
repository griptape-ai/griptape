from __future__ import annotations

from os import path
from typing import Optional

from attrs import define, field
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import ImageToImageGenerationEngine
from griptape.loaders.image_loader import ImageLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class ImageModifier(BaseTool):
    """ImageModifier is a tool that can be used to modify an image.

    Attributes:
        image_modification_engine: The engine used to modify the image.
        output_dir: If provided, the modified image will be written to disk in output_dir.

    """

    image_modification_engine: ImageToImageGenerationEngine = field(kw_only=True)
    output_dir: Optional[str] = field(default=None, kw_only=True)

    @activity(
        config={
            "description": "Can be used to modify an image.",
            "schema": Schema(
                {
                    Literal("image_path", description="The path to a png image to modify."): str,
                    Literal(
                        "prompts", description="A detailed list of modifications to make to the provided image."
                    ): list[str],
                    Literal(
                        "negative_prompts",
                        description="A detailed list of features and descriptions to avoid in the modifications.",
                    ): list[str],
                }
            ),
        }
    )
    def modify_image(self, params: dict) -> ImageArtifact | ErrorArtifact:
        image_path = params["values"]["image_path"]
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]

        input_image = ImageLoader().load(image_path)

        try:
            image_artifact = self.image_modification_engine.modify_image(
                input_image, prompts=prompts, negative_prompts=negative_prompts
            )

            if self.output_dir is not None:
                self._write_to_file(image_artifact)

            return image_artifact

        except Exception as e:
            return ErrorArtifact(value=str(e))

    @activity(
        config={
            "description": "Can be used to modify an image.",
            "schema": Schema(
                {
                    Literal("image_path", description="The path to a png image to modify."): str,
                    Literal("mask_path", description="The path to a png mask image to use for modifications."): str,
                    Literal(
                        "prompts", description="A detailed list of modifications to make to the provided image."
                    ): list[str],
                    Literal(
                        "negative_prompts",
                        description="A detailed list of features and descriptions to avoid in the modifications.",
                    ): list[str],
                }
            ),
        }
    )
    def modify_image_with_mask(self, params: dict) -> ImageArtifact | ErrorArtifact:
        image_path = params["values"]["image_path"]
        mask_path = params["values"]["mask_path"]
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]

        input_image = ImageLoader().load(image_path)
        mask_image = ImageLoader().load(mask_path)

        try:
            image_artifact = self.image_modification_engine.modify_image(
                input_image, mask_image=mask_image, prompts=prompts, negative_prompts=negative_prompts
            )

            if self.output_dir is not None:
                self._write_to_file(image_artifact)

            return image_artifact

        except Exception as e:
            return ErrorArtifact(value=str(e))

    def _write_to_file(self, image_artifact: ImageArtifact) -> None:
        outfile = path.join(self.output_dir, image_artifact.name)
        with open(outfile, "wb") as f:
            f.write(image_artifact.value)
