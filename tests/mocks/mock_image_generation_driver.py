from typing import Optional
from attr import define
from griptape.artifacts import ImageArtifact
from griptape.drivers.image_generation.base_image_generation_driver import BaseImageGenerationDriver


@define
class MockImageGenerationDriver(BaseImageGenerationDriver):
    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        return ImageArtifact(value="mock image", width=512, height=512)

    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        return ImageArtifact(value="mock image", width=512, height=512)

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        return ImageArtifact(value="mock image", width=512, height=512)

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        return ImageArtifact(value="mock image", width=512, height=512)
