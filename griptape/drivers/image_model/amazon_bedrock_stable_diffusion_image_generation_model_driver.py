from __future__ import annotations

import base64
from typing import Optional, TYPE_CHECKING

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseTextToImageGenerationDriver, BaseImageToImageGenerationDriver


@define
class AmazonBedrockStableDiffusionImageGenerationModelDriver(
    BaseTextToImageGenerationDriver, BaseImageToImageGenerationDriver
):
    """Image generation model driver for Stable Diffusion models on Amazon Bedrock.

    Attributes:
        cfg_scale: Specifies how strictly image generation follows the provided prompt. Defaults to 7.
        mask_source: Specifies mask image configuration for image-to-image generations. Defaults to "MASK_IMAGE_BLACK".
        style_preset: If provided, specifies a specific image generation style preset.
        clip_guidance_preset: If provided, requests a specific clip guidance preset to be used in the diffusion process.
        sampler: If provided, requests a specific sampler to be used in the diffusion process.
        steps: If provided, specifies the number of diffusion steps to use in the image generation.
        start_schedule: If provided, specifies the start_schedule parameter used in image-to-image generation.

    For more information on all supported paramaters, see the Stable Diffusion documentation:
        https://platform.stability.ai/docs/api-reference#tag/v1generation
    """

    cfg_scale: int = field(default=7, kw_only=True)
    mask_source: str = field(default="MASK_IMAGE_BLACK", kw_only=True)
    style_preset: Optional[str] = field(default=None, kw_only=True)
    clip_guidance_preset: Optional[str] = field(default=None, kw_only=True)
    sampler: Optional[str] = field(default=None, kw_only=True)
    steps: Optional[int] = field(default=None, kw_only=True)
    start_schedule: Optional[float] = field(default=None, kw_only=True)

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
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
            "width": image_width,
            "height": image_height,
        }

        if self.steps is not None:
            request["steps"] = self.steps

        if seed is not None:
            request["seed"] = seed

        return request

    def image_to_image_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask_image: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
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
            "width": image.width,
            "height": image.height,
            "init_image": image.base64,
        }

        if self.steps is not None:
            request["steps"] = self.steps

        if seed is not None:
            request["seed"] = seed

        if mask_image is not None:
            request["mask_source"] = self.mask_source
            request["mask_image"] = mask_image.base64

        if self.start_schedule is not None:
            request["start_schedule"] = self.start_schedule

        return request

    def get_generated_image(self, response: dict) -> bytes:
        image_response = response["artifacts"][0]
        if image_response.get("finishReason") != "SUCCESS":
            raise ValueError(f"Image generation failed: {image_response.get('finishReason')}")

        return base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))
