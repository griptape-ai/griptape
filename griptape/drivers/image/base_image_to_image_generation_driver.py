from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from attr import define

from griptape.artifacts import ImageArtifact

from .base_image_generation_driver import BaseImageGenerationDriver


@define
class BaseImageToImageGenerationDriver(BaseImageGenerationDriver):
    def image_to_image_generation(
        self,
        input_image: ImageArtifact,
        prompts: list[str],
        mask_image: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                return self.try_image_to_image_generation(
                    input_image, prompts=prompts, mask_image=mask_image, negative_prompts=negative_prompts
                )

    @abstractmethod
    def try_image_to_image_generation(
        self,
        image: ImageArtifact,
        prompts: list[str],
        mask_image: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        ...
