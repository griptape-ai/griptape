from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.tools import BaseImageGenerationTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import ErrorArtifact, ImageArtifact
    from griptape.drivers import BaseImageGenerationDriver


@define
class PromptImageGenerationTool(BaseImageGenerationTool):
    """A tool that can be used to generate an image from a text prompt.

    Attributes:
        image_generation_driver: The image generation driver used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True)

    @activity(
        config={
            "description": "Generates an image from text prompts.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseImageGenerationTool.PROMPT_DESCRIPTION): str,
                    Literal("negative_prompt", description=BaseImageGenerationTool.NEGATIVE_PROMPT_DESCRIPTION): str,
                }
            ),
        },
    )
    def generate_image(self, params: dict[str, dict[str, str]]) -> ImageArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]
        negative_prompt = params["values"]["negative_prompt"]

        output_artifact = self.image_generation_driver.run_text_to_image(
            prompts=[prompt], negative_prompts=[negative_prompt]
        )

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
