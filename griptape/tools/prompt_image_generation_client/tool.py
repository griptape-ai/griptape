from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.tools import BaseImageGenerationClient
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import ErrorArtifact, ImageArtifact
    from griptape.engines import PromptImageGenerationEngine


@define
class PromptImageGenerationClient(BaseImageGenerationClient):
    """A tool that can be used to generate an image from a text prompt.

    Attributes:
        engine: The prompt image generation engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    engine: PromptImageGenerationEngine = field(kw_only=True)

    @activity(
        config={
            "description": "Generates an image from text prompts.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationClient.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationClient.NEGATIVE_PROMPT_DESCRIPTION): str,
                }
            ),
        },
    )
    def generate_image(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]

        output_artifact = self.engine.run(prompts=[prompt], negative_prompts=[negative_prompt])

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
