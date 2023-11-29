from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from attr import define

from griptape.artifacts import ImageArtifact

from .base_image_generation_driver import BaseImageGenerationDriver


@define
class BaseTextToImageGenerationDriver(BaseImageGenerationDriver):
    def generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                return self.try_generate_image(prompts=prompts, negative_prompts=negative_prompts)

    @abstractmethod
    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...
