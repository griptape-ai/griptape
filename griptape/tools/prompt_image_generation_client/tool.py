from __future__ import annotations

from attrs import define, field
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import PromptImageGenerationEngine
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.mixins import ImageArtifactFileOutputMixin


@define
class PromptImageGenerationClient(ImageArtifactFileOutputMixin, BaseTool):
    """A tool that can be used to generate an image from a text prompt.

    Attributes:
        engine: The prompt image generation engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    engine: PromptImageGenerationEngine = field(kw_only=True)

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
    def generate_image(self, params: dict[str, dict[str, list[str]]]) -> ImageArtifact | ErrorArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]

        output_artifact = self.engine.run(prompts=prompts, negative_prompts=negative_prompts)

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
