from __future__ import annotations

import os
from typing import Literal, Optional

import requests
from attrs import Factory, define, field, fields_dict

from griptape.artifacts import ImageArtifact
from griptape.drivers.image_generation import BaseImageGenerationDriver
from griptape.utils.griptape_cloud import griptape_cloud_url


@define
class GriptapeCloudImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for the OpenAI image generation API.

    Attributes:
        model: Image generation model, 'gpt-image-1' or 'dall-e-3'. Defaults to 'dall-e-3'.
        base_url: Griptape Cloud API URL.
        api_key: Griptape Cloud API Key.
        headers: Headers for Griptape Cloud request. Overwrites api_key.
        image_size: Size of the generated image. Must be one of the following, depending on the requested model:
            dall-e-3: [1024x1024, 1024x1792, 1792x1024]
            gpt-image-1: [1024x1024, 1536x1024, 1024x1536, auto]
        style: Optional and only supported for dall-e-3, can be either 'vivid' or 'natural'.
        quality: Optional and only supported for dall-e-3. Accepts 'standard', 'hd'.
        background: Optional and only supported for gpt-image-1. Can be either 'transparent', 'opaque', or 'auto'.
        moderation: Optional and only supported for gpt-image-1. Can be either 'low' or 'auto'.
        output_compression: Optional and only supported for gpt-image-1. Can be an integer between 0 and 100.
        output_format: Optional and only supported for gpt-image-1. Can be either 'png' or 'jpeg'.
    """

    model: str = field(default="dall-e-3", kw_only=True, metadata={"serializable": True})
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    image_size: Optional[Literal["1024x1024", "1536x1024", "1024x1536", "1024x1792", "1792x1024", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    style: Optional[Literal["vivid", "natural"]] = field(
        default=None, kw_only=True, metadata={"serializable": True, "model_allowlist": ["dall-e-3"]}
    )
    quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True, "model_allowlist": ["dall-e-3"]},
    )
    background: Optional[Literal["transparent", "opaque", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True, "model_allowlist": ["gpt-image-1"]},
    )
    moderation: Optional[Literal["low", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True, "model_allowlist": ["gpt-image-1"]},
    )
    output_compression: Optional[int] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True, "model_allowlist": ["gpt-image-1"]},
    )
    output_format: Optional[Literal["png", "jpeg"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True, "model_allowlist": ["gpt-image-1"]},
    )
    model_configuration: dict = field(
        default=Factory(dict),
        kw_only=True,
        metadata={"serializable": True},
    )

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        url = griptape_cloud_url(self.base_url, "api/images/generations")

        response = requests.post(
            url,
            headers=self.headers,
            json={
                "prompts": prompts,
                "driver_configuration": self._build_driver_configuration(),
            },
        )
        response.raise_for_status()
        response = response.json()

        return ImageArtifact.from_dict(response["artifact"])

    def _build_driver_configuration(self) -> dict:
        """Builds parameters while considering field metadata and None values.

        Field will be added to the params dictionary if all conditions are met:
            - The field value is not None
            - The model_allowlist is None or the model is in the allowlist
        """
        values = [
            "model",
            "image_size",
            "quality",
            "style",
            "background",
            "moderation",
            "output_compression",
            "output_format",
        ]

        params = {}
        fields = fields_dict(self.__class__)

        for value in values:
            metadata = fields[value].metadata
            model_allowlist = metadata.get("model_allowlist")

            field_value = getattr(self, value, None)

            allowlist_condition = model_allowlist is None or self.model in model_allowlist

            if field_value is not None and allowlist_condition:
                params[value] = field_value
        return {**params, **self.model_configuration}

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        if self.model != "gpt-image-1":
            raise ValueError(f"Image variation is only supported with gpt-image-1 model, but {self.model} was provided")

        url = griptape_cloud_url(self.base_url, "api/images/variations")

        response = requests.post(
            url,
            headers=self.headers,
            json={
                "prompts": prompts,
                "image_base64": image.base64,
                "driver_configuration": self._build_driver_configuration(),
            },
        )
        response.raise_for_status()
        response = response.json()

        return ImageArtifact.from_dict(response["artifact"])

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
