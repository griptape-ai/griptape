from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.drivers import BaseImageGenerationModelDriver

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define
class BedrockStableDiffusionImageGenerationModelDriver(BaseImageGenerationModelDriver):
    """Image generation model driver for Stable Diffusion models on Amazon Bedrock.

    For more information on all supported parameters, see the Stable Diffusion documentation:
        https://platform.stability.ai/docs/api-reference#tag/v1generation

    Attributes:
        cfg_scale: Specifies how strictly image generation follows the provided prompt. Defaults to 7.
        mask_source: Specifies mask image configuration for image-to-image generations. Defaults to "MASK_IMAGE_BLACK".
        style_preset: If provided, specifies a specific image generation style preset.
        clip_guidance_preset: If provided, requests a specific clip guidance preset to be used in the diffusion process.
        sampler: If provided, requests a specific sampler to be used in the diffusion process.
        steps: If provided, specifies the number of diffusion steps to use in the image generation.
        start_schedule: If provided, specifies the start_schedule parameter used to determine the influence of the input
            image in image-to-image generation.
    """

    cfg_scale: int = field(default=7, kw_only=True, metadata={"serializable": True})
    style_preset: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    clip_guidance_preset: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    sampler: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    steps: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    start_schedule: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        return self._request_parameters(
            prompts,
            width=image_width,
            height=image_height,
            negative_prompts=negative_prompts,
            seed=seed,
        )

    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        return self._request_parameters(prompts, image=image, negative_prompts=negative_prompts, seed=seed)

    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        return self._request_parameters(
            prompts,
            image=image,
            mask=mask,
            mask_source="MASK_IMAGE_BLACK",
            negative_prompts=negative_prompts,
            seed=seed,
        )

    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        return self._request_parameters(
            prompts,
            image=image,
            mask=mask,
            mask_source="MASK_IMAGE_WHITE",
            negative_prompts=negative_prompts,
            seed=seed,
        )

    def _request_parameters(
        self,
        prompts: list[str],
        width: Optional[int] = None,
        height: Optional[int] = None,
        image: Optional[ImageArtifact] = None,
        mask: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
        mask_source: Optional[str] = None,
    ) -> dict:
        if negative_prompts is None:
            negative_prompts = []

        text_prompts = [{"text": prompt, "weight": 1.0} for prompt in prompts]
        text_prompts += [{"text": negative_prompt, "weight": -1.0} for negative_prompt in negative_prompts]

        request = {
            "text_prompts": text_prompts,
            "cfg_scale": self.cfg_scale,
            "style_preset": self.style_preset,
            "clip_guidance_preset": self.clip_guidance_preset,
            "sampler": self.sampler,
            "steps": self.steps,
            "seed": seed,
            "start_schedule": self.start_schedule,
        }

        if image is not None:
            request["init_image"] = image.base64
            request["width"] = image.width
            request["height"] = image.height
        else:
            request["width"] = width
            request["height"] = height

        if mask is not None:
            if not mask_source:
                raise ValueError("mask_source must be provided when mask is provided")

            request["mask_source"] = mask_source
            request["mask_image"] = mask.base64

        request = {k: v for k, v in request.items() if v is not None}

        return request

    def get_generated_image(self, response: dict) -> bytes:
        image_response = response["artifacts"][0]

        # finishReason may be SUCCESS, CONTENT_FILTERED, or ERROR.
        if image_response.get("finishReason") == "ERROR":
            raise Exception(f"Image generation failed: {image_response.get('finishReason')}")
        elif image_response.get("finishReason") == "CONTENT_FILTERED":
            logging.warning("Image generation triggered content filter and may be blurred")

        return base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))
