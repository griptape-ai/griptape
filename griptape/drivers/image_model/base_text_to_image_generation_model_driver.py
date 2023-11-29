from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from attr import define

from griptape.drivers import BaseImageGenerationModelDriver


@define
class BaseTextToImageGenerationModelDriver(BaseImageGenerationModelDriver):
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
