from attr import define, field, Factory
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver, OpenAiDalleImageGenerationDriver
from griptape.engines.image_generation.base_image_generation_engine import BaseImageGenerationEngine
from griptape.engines.image_generation.openai_dalle_image_generation_engine import OpenAiDalleImageGenerationEngine
from griptape.tasks import BaseTextInputTask


@define
class ImageGenerationTask(BaseTextInputTask):
    image_generation_engine: BaseImageGenerationEngine = field(
        default=Factory(lambda self: OpenAiDalleImageGenerationEngine()), kw_only=True
    )

    def run(self) -> ImageArtifact:
        images = self.image_generation_engine.generate_image(self.input.to_text())

        return images
