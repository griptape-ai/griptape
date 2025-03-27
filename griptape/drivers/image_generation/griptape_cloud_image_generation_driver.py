from __future__ import annotations

import os
from typing import Literal, Optional
from urllib.parse import urljoin

import requests
from attrs import Factory, define, field

from griptape.artifacts import ImageArtifact
from griptape.drivers.image_generation import BaseImageGenerationDriver


@define
class GriptapeCloudImageGenerationDriver(BaseImageGenerationDriver):
    model: Optional[str] = field(default=None, kw_only=True)
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    style: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    quality: Literal["standard", "hd"] = field(default="standard", kw_only=True, metadata={"serializable": True})
    image_size: Literal["1024x1024", "1024x1792", "1792x1024"] = field(
        default="1024x1024", kw_only=True, metadata={"serializable": True}
    )

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        url = urljoin(self.base_url.strip("/"), "/api/images/generations")

        response = requests.post(
            url,
            headers=self.headers,
            json={
                "prompts": prompts,
                "driver_configuration": {
                    "model": self.model,
                    "image_size": self.image_size,
                    "quality": self.quality,
                    "style": self.style,
                },
            },
        )
        response.raise_for_status()
        response = response.json()

        return ImageArtifact.from_dict(response["artifact"])

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support image variation")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support inpainting")

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support outpainting")
