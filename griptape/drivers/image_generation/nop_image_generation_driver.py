from typing import Optional
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import NopException


class NopImageGenerationDriver(BaseEmbeddingDriver):
    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        raise NopException(__class__.__name__, "try_text_to_image")

    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        raise NopException(__class__.__name__, "try_image_variation")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NopException(__class__.__name__, "try_image_inpainting")

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NopException(__class__.__name__, "try_image_outpainting")
