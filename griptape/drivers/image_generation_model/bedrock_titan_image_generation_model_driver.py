from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseImageGenerationModelDriver

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define
class BedrockTitanImageGenerationModelDriver(BaseImageGenerationModelDriver):
    """Image Generation Model Driver for Amazon Bedrock Titan Image Generator.

    Attributes:
        quality: The quality of the generated image, defaults to standard.
        cfg_scale: Specifies how strictly image generation follows the provided prompt. Defaults to 7, (1.0 to 10.0].
        outpainting_mode: Specifies the outpainting mode, defaults to PRECISE.
    """

    quality: str = field(default="standard", kw_only=True, metadata={"serializable": True})
    cfg_scale: int = field(default=7, kw_only=True, metadata={"serializable": True})
    outpainting_mode: str = field(default="PRECISE", kw_only=True, metadata={"serializable": True})

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image_width,
                "height": image_height,
                "cfgScale": self.cfg_scale,
            },
        }

        if negative_prompts:
            request["textToImageParams"]["negativeText"] = ", ".join(negative_prompts)

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return self._add_common_params(request, image_width, image_height, seed=seed)

    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": "IMAGE_VARIATION",
            "imageVariationParams": {"text": prompt, "images": [image.base64]},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image.width,
                "height": image.height,
                "cfgScale": self.cfg_scale,
            },
        }

        if negative_prompts:
            request["imageVariationParams"]["negativeText"] = ", ".join(negative_prompts)

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return self._add_common_params(request, image.width, image.height, seed=seed)

    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": "INPAINTING",
            "inPaintingParams": {"text": prompt, "image": image.base64, "maskImage": mask.base64},
        }

        if negative_prompts:
            request["inPaintingParams"]["negativeText"] = ", ".join(negative_prompts)

        return self._add_common_params(request, image.width, image.height, seed=seed)

    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": "OUTPAINTING",
            "outPaintingParams": {
                "text": prompt,
                "image": image.base64,
                "maskImage": mask.base64,
                "outPaintingMode": self.outpainting_mode,
            },
        }

        if negative_prompts:
            request["outPaintingParams"]["negativeText"] = ", ".join(negative_prompts)

        return self._add_common_params(request, image.width, image.height, seed=seed)

    def get_generated_image(self, response: dict) -> bytes:
        b64_image_data = response["images"][0]

        return base64.decodebytes(bytes(b64_image_data, "utf-8"))

    def _add_common_params(self, request: dict[str, Any], width: int, height: int, seed: Optional[int] = None) -> dict:
        request["imageGenerationConfig"] = {
            "numberOfImages": 1,
            "quality": self.quality,
            "width": width,
            "height": height,
            "cfgScale": self.cfg_scale,
        }

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return request
