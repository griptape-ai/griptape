from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Literal, Optional

import openai
from attrs import Factory, define, field, fields_dict

from griptape.drivers.image_generation import BaseImageGenerationDriver
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from openai.types.images_response import ImagesResponse

    from griptape.artifacts import ImageArtifact


@define
class OpenAiImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for the OpenAI image generation API.

    Attributes:
        model: OpenAI model, for example 'dall-e-2' or 'dall-e-3'.
        api_type: OpenAI API type, for example 'open_ai' or 'azure'.
        api_version: API version.
        base_url: API URL.
        api_key: OpenAI API key.
        organization: OpenAI organization ID.
        style: Optional and only supported for dall-e-3, can be either 'vivid' or 'natural'.
        quality: Optional and only supported for dall-e-3. Accepts 'standard', 'hd'.
        image_size: Size of the generated image. Must be one of the following, depending on the requested model:
            dall-e-2: [256x256, 512x512, 1024x1024]
            dall-e-3: [1024x1024, 1024x1792, 1792x1024]
            gpt-image-1: [1024x1024, 1536x1024, 1024x1536, auto]
        response_format: The response format. Currently only supports 'b64_json' which will return
            a base64 encoded image in a JSON object.
        background: Optional and only supported for gpt-image-1. Can be either 'transparent', 'opaque', or 'auto'.
        moderation: Optional and only supported for gpt-image-1. Can be either 'low' or 'auto'.
        output_compression: Optional and only supported for gpt-image-1. Can be an integer between 0 and 100.
        output_format: Optional and only supported for gpt-image-1. Can be either 'png' or 'jpeg'.
    """

    api_type: Optional[str] = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    organization: Optional[str] = field(default=openai.organization, kw_only=True, metadata={"serializable": True})
    style: Optional[Literal["vivid", "natural"]] = field(
        default=None, kw_only=True, metadata={"serializable": True, "model_allowlist": ["dall-e-3"]}
    )
    quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    image_size: Optional[Literal["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
    )
    response_format: Literal["b64_json"] = field(
        default="b64_json",
        kw_only=True,
        metadata={"serializable": True, "model_denylist": ["gpt-image-1"]},
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
    _client: Optional[openai.OpenAI] = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(
            lambda: (
                openai.BadRequestError,
                openai.AuthenticationError,
                openai.PermissionDeniedError,
                openai.NotFoundError,
                openai.ConflictError,
                openai.UnprocessableEntityError,
            ),
        ),
        kw_only=True,
    )

    @image_size.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_image_size(self, attribute: str, value: str | None) -> None:
        """Validates the image size based on the model.

        Must be one of `1024x1024`, `1536x1024` (landscape), `1024x1536` (portrait), or `auto` (default value) for
        `gpt-image-1`, one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, and
        one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.

        """
        if value is None:
            return

        if self.model.startswith("gpt-image"):
            allowed_sizes = ("1024x1024", "1536x1024", "1024x1536", "auto")
        elif self.model == "dall-e-2":
            allowed_sizes = ("256x256", "512x512", "1024x1024")
        elif self.model == "dall-e-3":
            allowed_sizes = ("1024x1024", "1792x1024", "1024x1792")
        else:
            raise NotImplementedError(f"Image size validation not implemented for model {self.model}")

        if value is not None and value not in allowed_sizes:
            raise ValueError(f"Image size, {value}, must be one of the following: {allowed_sizes}")

    @lazy_property()
    def client(self) -> openai.OpenAI:
        return openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization)

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        prompt = ", ".join(prompts)

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            n=1,
            **self._build_model_params(
                {
                    "size": "image_size",
                    "quality": "quality",
                    "style": "style",
                    "response_format": "response_format",
                    "background": "background",
                    "moderation": "moderation",
                    "output_compression": "output_compression",
                    "output_format": "output_format",
                }
            ),
        )

        return self._parse_image_response(response, prompt)

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        """Creates a variation of an image.

        Only supported by for dall-e-2. Requires image size to be one of the following:
            [256x256, 512x512, 1024x1024]
        """
        if self.model != "dall-e-2":
            raise NotImplementedError("Image variation only supports dall-e-2")
        response = self.client.images.create_variation(
            image=image.value,
            n=1,
            response_format=self.response_format,
            size=self.image_size,  # pyright: ignore[reportArgumentType]
        )

        return self._parse_image_response(response, "")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        prompt = ", ".join(prompts)
        response = self.client.images.edit(
            prompt=prompt,
            image=image.value,
            mask=mask.value,
            **self._build_model_params(
                {
                    "size": "image_size",
                    "response_format": "response_format",
                }
            ),
        )

        return self._parse_image_response(response, prompt)

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support outpainting")

    def _parse_image_response(self, response: ImagesResponse, prompt: str) -> ImageArtifact:
        from griptape.loaders.image_loader import ImageLoader

        if response.data is None or response.data[0] is None or response.data[0].b64_json is None:
            raise Exception("Failed to generate image")

        image_data = base64.b64decode(response.data[0].b64_json)

        image_artifact = ImageLoader().parse(image_data)

        image_artifact.meta["prompt"] = prompt
        image_artifact.meta["model"] = self.model

        return image_artifact

    def _build_model_params(self, values: dict) -> dict:
        """Builds parameters while considering field metadata and None values.

        Args:
            values: A dictionary mapping parameter names to field names.

        Field will be added to the params dictionary if all conditions are met:
            - The field value is not None
            - The model_allowlist is None or the model is in the allowlist
            - The model_denylist is None or the model is not in the denylist
        """
        params = {}

        fields = fields_dict(self.__class__)
        for param_name, field_name in values.items():
            metadata = fields[field_name].metadata
            model_allowlist = metadata.get("model_allowlist")
            model_denylist = metadata.get("model_denylist")

            field_value = getattr(self, field_name, None)

            allowlist_condition = model_allowlist is None or self.model in model_allowlist
            denylist_condition = model_denylist is None or self.model not in model_denylist

            if field_value is not None and allowlist_condition and denylist_condition:
                params[param_name] = field_value
        return params
