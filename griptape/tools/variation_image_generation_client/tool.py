from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.loaders import ImageLoader
from griptape.tools.base_image_generation_client import BaseImageGenerationClient
from griptape.utils.decorators import activity
from griptape.utils.load_artifact_from_memory import load_artifact_from_memory

if TYPE_CHECKING:
    from griptape.engines import VariationImageGenerationEngine


@define
class VariationImageGenerationClient(BaseImageGenerationClient):
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
            "description": "Generates a variation of a given input image file.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationClient.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationClient.NEGATIVE_PROMPT_DESCRIPTION): str,
                    Literal(
                        "image_file",
                        description="The path to an image file to be used as a base to generate variations from.",
                    ): str,
                },
            ),
        },
    )
    def image_variation_from_file(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]
        image_file = params["values"]["image_file"]

        image_artifact = self.image_loader.load(Path(image_file).read_bytes())

        if isinstance(image_artifact, ErrorArtifact):
            return image_artifact

        return self._generate_variation(prompt, negative_prompt, image_artifact)

    @activity(
        config={
            "description": "Generates a variation of a given input image artifact in memory.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationClient.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationClient.NEGATIVE_PROMPT_DESCRIPTION): str,
                    "memory_name": str,
                    "artifact_namespace": str,
                    "artifact_name": str,
                },
            ),
        },
    )
    def image_variation_from_memory(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]
        artifact_namespace = params["values"]["artifact_namespace"]
        artifact_name = params["values"]["artifact_name"]
        memory = self.find_input_memory(params["values"]["memory_name"])

        if memory is None:
            return ErrorArtifact("memory not found")

        try:
            image_artifact = load_artifact_from_memory(memory, artifact_namespace, artifact_name, ImageArtifact)
        except ValueError as e:
            return ErrorArtifact(str(e))

        return self._generate_variation(prompt, negative_prompt, cast(ImageArtifact, image_artifact))

    def _generate_variation(
        self, prompt: str, negative_prompt: str, image_artifact: ImageArtifact
    ) -> ImageArtifact | ErrorArtifact:
        output_artifact = self.engine.run(prompts=[prompt], negative_prompts=[negative_prompt], image=image_artifact)

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
