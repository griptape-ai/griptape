import base64
from typing import Optional

from attr import field, define

from griptape.drivers import BaseImageGenerationModelDriver


@define
class AmazonBedrockStableDiffusionImageGenerationModelDriver(BaseImageGenerationModelDriver):
    cfg_scale: int = field(default=7, kw_only=True)
    style_preset: Optional[str] = field(default=None, kw_only=True)
    clip_guidance_preset: Optional[str] = field(default=None, kw_only=True)
    sampler: Optional[str] = field(default=None, kw_only=True)
    steps: Optional[int] = field(default=None, kw_only=True)

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

    def get_generated_image(self, response: dict) -> bytes:
        image_response = response["artifacts"][0]
        if image_response.get("finishReason") != "SUCCESS":
            raise ValueError(f"Image generation failed: {image_response.get('finishReason')}")

        return base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))
