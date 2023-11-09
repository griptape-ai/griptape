from attr import field, define
from griptape.drivers import BaseImageGenerationDriver


@define
class ImageGenerationEngine:
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True)

    def generate_image(self, prompts: list[str], negative_prompts: list[str], **kwargs):
        return self.image_generation_driver.generate_image(prompts, negative_prompts, **kwargs)
