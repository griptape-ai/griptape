from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from attrs import define

if TYPE_CHECKING:
    from PIL.Image import Image


@define
class BaseDiffusionImageGenerationPipelineDriver(ABC):
    @abstractmethod
    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any: ...

    @abstractmethod
    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]: ...

    @abstractmethod
    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict: ...

    @property
    @abstractmethod
    def output_image_dimensions(self) -> tuple[int, int]: ...
