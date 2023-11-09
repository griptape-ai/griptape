from __future__ import annotations
from attr import define, field
from griptape.artifacts import ImageArtifact, ErrorArtifact
from griptape.engines import ImageGenerationEngine
from griptape.tasks import BaseTextInputTask


@define
class ImageGenerationTask(BaseTextInputTask):
    image_generation_engine: ImageGenerationEngine = field(kw_only=True)

    def run(self) -> ImageArtifact | ErrorArtifact:
        try:
            image_artifact = self.image_generation_engine.generate_image(
                prompts=[self.input.to_text()], negative_prompts=[]
            )

            return image_artifact

        except Exception as e:
            return ErrorArtifact(str(e))
