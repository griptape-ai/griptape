from __future__ import annotations

from os import path
from typing import Optional

from attrs import define, field
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines import ImageGenerationEngine
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class ImageGenerator(BaseTool):
    """ImageGenerator is a tool that can be used to generate an image.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.

    """

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    output_dir: Optional[str] = field(default=None, kw_only=True)

    @activity(
        config={
            "description": "Can be used to generate an image.",
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
    def generate_image(self, params: dict) -> ImageArtifact | ErrorArtifact:
        prompts = params["values"]["prompts"]
        negative_prompts = params["values"]["negative_prompts"]

        try:
            image_artifact = self.image_generation_engine.generate_image(
                prompts=prompts, negative_prompts=negative_prompts
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
