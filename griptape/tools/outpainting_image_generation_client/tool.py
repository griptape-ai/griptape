from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.loaders import ImageLoader
from griptape.tools import BaseImageGenerationClient
from griptape.utils.decorators import activity
from griptape.utils.load_artifact_from_memory import load_artifact_from_memory

if TYPE_CHECKING:
    from griptape.engines import OutpaintingImageGenerationEngine


@define
class OutpaintingImageGenerationClient(BaseImageGenerationClient):
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
            "description": "Modifies an image outside a specified mask area using image and mask files.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationClient.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationClient.NEGATIVE_PROMPT_DESCRIPTION): str,
                    Literal(
                        "image_file",
                        description="The path to an image file to be used as a base to generate variations from.",
                    ): str,
                    Literal("mask_file", description="The path to mask image file."): str,
                },
            ),
        },
    )
    def image_outpainting_from_file(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]
        image_file = params["values"]["image_file"]
        mask_file = params["values"]["mask_file"]

        input_artifact = self.image_loader.load(Path(image_file).read_bytes())
        mask_artifact = self.image_loader.load(Path(mask_file).read_bytes())

        return self._generate_outpainting(prompt, negative_prompt, input_artifact, mask_artifact)

    @activity(
        config={
            "description": "Modifies an image outside a specified mask area using image and mask artifacts in memory.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationClient.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationClient.NEGATIVE_PROMPT_DESCRIPTION): str,
                    "memory_name": str,
                    "image_artifact_namespace": str,
                    "mask_artifact_namespace": str,
                },
            ),
        },
    )
    def image_outpainting_from_memory(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
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

        return self._generate_outpainting(
            prompt, negative_prompt, cast(ImageArtifact, image_artifact), cast(ImageArtifact, mask_artifact)
        )

    def _generate_outpainting(
        self, prompt: str, negative_prompt: str, image_artifact: ImageArtifact, mask_artifact: ImageArtifact
    ) -> ImageArtifact | ErrorArtifact:
        output_artifact = self.engine.run(
            prompts=[prompt], negative_prompts=[negative_prompt], image=image_artifact, mask=mask_artifact
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
