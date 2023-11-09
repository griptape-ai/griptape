from attrs import define, field, Factory
from schema import Schema, Literal
from griptape.artifacts import ErrorArtifact, ImageArtifact
from griptape.engines.image_generation.image_generation_engine import ImageGenerationEngine
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class ImageGenerator(BaseTool):
    image_generation_engine: ImageGenerationEngine = field(kw_only=True)

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
            image = self.image_generation_engine.generate_image(prompts=prompts, negative_prompts=negative_prompts)

            return image

        except Exception as e:
            return ErrorArtifact(value=str(e))
