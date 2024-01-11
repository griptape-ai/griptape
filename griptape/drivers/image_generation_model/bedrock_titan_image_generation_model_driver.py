from __future__ import annotations

import base64

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationModelDriver


@define
class BedrockTitanImageGenerationModelDriver(BaseImageGenerationModelDriver):
    """Image Generation Model Driver for Amazon Bedrock Titan Image Generator.

    Attributes:
        quality: The quality of the generated image, defaults to standard.
        cfg_scale: Specifies how strictly image generation follows the provided prompt. Defaults to 7, (1.0 to 10.0].
        outpainting_mode: Specifies the outpainting mode, defaults to PRECISE.
    """

    quality: str = field(default="standard", kw_only=True)
    cfg_scale: int = field(default=7, kw_only=True)
    outpainting_mode: str = field(default="PRECISE", kw_only=True)

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
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

        return request

    def image_variation_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
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

        return request

    def image_inpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": "INPAINTING",
            "inPaintingParams": {"text": prompt, "image": image.base64, "maskImage": mask.base64},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image.width,
                "height": image.height,
                "cfgScale": self.cfg_scale,
            },
        }

        if negative_prompts:
            request["inPaintingParams"]["negativeText"] = ", ".join(negative_prompts)

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return request

    def image_outpainting_request_parameters(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        seed: int | None = None,
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
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image.width,
                "height": image.height,
                "cfgScale": self.cfg_scale,
            },
        }

        if negative_prompts:
            request["outPaintingParams"]["negativeText"] = ", ".join(negative_prompts)

        if seed:
            request["imageGenerationConfig"]["seed"] = seed

        return request

    def get_generated_image(self, response: dict) -> bytes:
        b64_image_data = response["images"][0]

        return base64.decodebytes(bytes(b64_image_data, "utf-8"))
