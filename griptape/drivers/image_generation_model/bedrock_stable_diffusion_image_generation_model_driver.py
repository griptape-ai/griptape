from __future__ import annotations

import base64

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationModelDriver


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

    cfg_scale: int = field(default=7, kw_only=True)
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
        return self._request_parameters(
            prompts, width=image_width, height=image_height, negative_prompts=negative_prompts, seed=seed
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
        }

        if image:
            request["init_image"] = image.value
            request["width"] = image.width
            request["height"] = image.height
        else:
            request["width"] = width
            request["height"] = height

        if self.steps:
            request["steps"] = self.steps

        if seed:
            request["seed"] = seed

        if mask:
            if not mask_source:
                raise ValueError("mask_source must be provided when mask is provided")

            request["mask_source"] = mask_source
            request["mask_image"] = mask.value

        if self.start_schedule:
            request["start_schedule"] = self.start_schedule

        return request

    def get_generated_image(self, response: dict) -> bytes:
        image_response = response["artifacts"][0]
        if image_response.get("finishReason") != "SUCCESS":
            raise ValueError(f"Image generation failed: {image_response.get('finishReason')}")

        return base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))
