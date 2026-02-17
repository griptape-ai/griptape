from __future__ import annotations

import os
from typing import Literal, Optional

import requests
from attrs import Factory, define, field, fields_dict

from griptape.artifacts import ImageArtifact
from griptape.drivers.image_generation import BaseImageGenerationDriver
from griptape.utils.griptape_cloud import griptape_cloud_url

ALLOWED_IMAGE_SIZES = ("1024x1024", "1536x1024", "1024x1536")
DEFAULT_MODEL = "gpt-image-1-mini"
SUPPORTED_MODELS = (DEFAULT_MODEL, "gpt-image-1.5")


@define
class GriptapeCloudImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for the OpenAI image generation API.

    Attributes:
        model: Image generation model. Supported values: 'gpt-image-1-mini', 'gpt-image-1.5'. Defaults to 'gpt-image-1-mini'.
        base_url: Griptape Cloud API URL.
        api_key: Griptape Cloud API Key.
        headers: Headers for Griptape Cloud request. Overwrites api_key.
        image_size: Size of the generated image. Must be one of: 1024x1024, 1024x1536, 1536x1024.
        quality: Optional quality level. Accepts 'low', 'medium', 'high'.
        background: Optional background setting. Can be either 'transparent', 'opaque', or 'auto'.
        moderation: Optional moderation level. Can be either 'low' or 'auto'.
        output_compression: Optional compression level. Can be an integer between 0 and 100.
        output_format: Optional output format. Can be either 'png' or 'jpeg'.
    """

    model: str = field(default=DEFAULT_MODEL, kw_only=True, metadata={"serializable": True})
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    image_size: Optional[Literal["1024x1024", "1536x1024", "1024x1536"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    quality: Optional[Literal["low", "medium", "high"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    background: Optional[Literal["transparent", "opaque", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    moderation: Optional[Literal["low", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    output_compression: Optional[int] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    output_format: Optional[Literal["png", "jpeg"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )

    @image_size.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_image_size(self, attribute: str, value: str | None) -> None:
        """Validates the image size.

        Must be one of `1024x1024`, `1536x1024` (landscape), or `1024x1536` (portrait).

        """
        if value is None:
            return

        if value not in ALLOWED_IMAGE_SIZES:
            raise ValueError(f"Image size, {value}, must be one of the following: {ALLOWED_IMAGE_SIZES}")

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
        return params

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(f"Image variation is only supported with {SUPPORTED_MODELS}, but {self.model} was provided")

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
