from typing import Optional
from attrs import define, field
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver
from griptape.exceptions import DummyException


@define
class DummyImageGenerationDriver(BaseImageGenerationDriver):
    model: str = field(init=False)

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        raise DummyException(__class__.__name__, "try_text_to_image")

    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        raise DummyException(__class__.__name__, "try_image_variation")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise DummyException(__class__.__name__, "try_image_inpainting")

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise DummyException(__class__.__name__, "try_image_outpainting")
