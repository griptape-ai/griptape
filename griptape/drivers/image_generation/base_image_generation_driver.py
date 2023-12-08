from abc import ABC, abstractmethod
from typing import Optional

from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.mixins import ExponentialBackoffMixin


@define
class BaseImageGenerationDriver(ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True)

    @abstractmethod
    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        ...
