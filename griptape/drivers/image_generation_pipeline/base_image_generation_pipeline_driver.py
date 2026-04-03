from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from attrs import define

if TYPE_CHECKING:
    from PIL.Image import Image


@define
class BaseDiffusionImageGenerationPipelineDriver(ABC):
    @abstractmethod
    def prepare_pipeline(self, model: str, device: str | None) -> Any: ...

    @abstractmethod
    def make_image_param(self, image: Image | None) -> dict[str, Image] | None: ...

    @abstractmethod
    def make_additional_params(self, negative_prompts: list[str] | None, device: str | None) -> dict: ...

    @property
    @abstractmethod
    def output_image_dimensions(self) -> tuple[int, int]: ...
