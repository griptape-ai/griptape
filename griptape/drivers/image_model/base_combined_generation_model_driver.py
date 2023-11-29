from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional

from attr import define

from griptape.artifacts import ImageArtifact


@define
class BaseCombinedGenerationModelDriver(ABC):
    @abstractmethod
    def image_to_image_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask_image: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
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
    def get_generated_image(self, response: dict) -> bytes:
        ...
