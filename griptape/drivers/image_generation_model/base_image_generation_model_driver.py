from abc import ABC, abstractmethod
from typing import Optional

from attr import define

from griptape.artifacts import ImageArtifact


@define
class BaseImageGenerationModelDriver(ABC):
    @abstractmethod
    def get_generated_image(self, response: dict) -> bytes:
        ...

    @abstractmethod
    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        ...

    @abstractmethod
    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ):
        ...

    @abstractmethod
    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ):
        ...

    @abstractmethod
    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ):
        ...
