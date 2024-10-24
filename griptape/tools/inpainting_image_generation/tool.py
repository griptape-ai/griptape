from __future__ import annotations

from typing import TYPE_CHECKING, cast

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.loaders import ImageLoader
from griptape.tools.base_image_generation_tool import BaseImageGenerationTool
from griptape.utils.decorators import activity
from griptape.utils.load_artifact_from_memory import load_artifact_from_memory

if TYPE_CHECKING:
    from griptape.drivers import BaseImageGenerationDriver


@define
class InpaintingImageGenerationTool(BaseImageGenerationTool):
    """A tool that can be used to generate prompted inpaintings of an image.

    Attributes:
        image_generation_driver: The image generation driver used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True)
    image_loader: ImageLoader = field(default=ImageLoader(), kw_only=True)

    @activity(
        config={
            "description": "Modifies an image within a specified mask area using image and mask files.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationTool.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationTool.NEGATIVE_PROMPT_DESCRIPTION): str,
                    Literal(
                        "image_file",
                        description="The path to an image file to be used as a base to generate variations from.",
                    ): str,
                    Literal("mask_file", description="The path to mask image file."): str,
                },
            ),
        },
    )
    def image_inpainting_from_file(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]
        image_file = params["values"]["image_file"]
        mask_file = params["values"]["mask_file"]

        input_artifact = self.image_loader.load(image_file)
        mask_artifact = self.image_loader.load(mask_file)

        return self._generate_inpainting(
            prompt, negative_prompt, cast(ImageArtifact, input_artifact), cast(ImageArtifact, mask_artifact)
        )

    @activity(
        config={
            "description": "Modifies an image within a specified mask area using image and mask artifacts in memory.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationTool.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationTool.NEGATIVE_PROMPT_DESCRIPTION): str,
                    "memory_name": str,
                    "image_artifact_namespace": str,
                    "image_artifact_name": str,
                    "mask_artifact_namespace": str,
                    "mask_artifact_name": str,
                },
            ),
        },
    )
    def image_inpainting_from_memory(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]
        image_artifact_namespace = params["values"]["image_artifact_namespace"]
        image_artifact_name = params["values"]["image_artifact_name"]
        mask_artifact_namespace = params["values"]["mask_artifact_namespace"]
        mask_artifact_name = params["values"]["mask_artifact_name"]
        memory = self.find_input_memory(params["values"]["memory_name"])

        if memory is None:
            return ErrorArtifact("memory not found")

        try:
            image_artifact = load_artifact_from_memory(
                memory,
                image_artifact_namespace,
                image_artifact_name,
                ImageArtifact,
            )
            mask_artifact = load_artifact_from_memory(
                memory,
                mask_artifact_namespace,
                mask_artifact_name,
                ImageArtifact,
            )
        except ValueError as e:
            return ErrorArtifact(str(e))

        return self._generate_inpainting(
            prompt, negative_prompt, cast(ImageArtifact, image_artifact), cast(ImageArtifact, mask_artifact)
        )

    def _generate_inpainting(
        self, prompt: str, negative_prompt: str, image_artifact: ImageArtifact, mask_artifact: ImageArtifact
    ) -> ImageArtifact:
        output_artifact = self.image_generation_driver.run_image_inpainting(
            prompts=[prompt], negative_prompts=[negative_prompt], image=image_artifact, mask=mask_artifact
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
