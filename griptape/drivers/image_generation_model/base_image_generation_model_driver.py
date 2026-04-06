from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from attrs import define

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define
class BaseImageGenerationModelDriver(SerializableMixin, ABC):
    @abstractmethod
    def get_generated_image(self, response: dict) -> bytes:
        pass

    @abstractmethod
    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        pass
