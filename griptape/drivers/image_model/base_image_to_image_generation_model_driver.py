from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from attr import define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationModelDriver


@define
class BaseImageToImageGenerationModelDriver(BaseImageGenerationModelDriver):
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
