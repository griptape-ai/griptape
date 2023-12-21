import base64
from typing import Any, Optional

from attr import field, define

from griptape.drivers import BaseImageGenerationModelDriver


@define
class AmazonBedrockTitanImageGenerationModelDriver(BaseImageGenerationModelDriver):
    task_type: str = field(default="TEXT_IMAGE", kw_only=True)
    quality: str = field(default="standard", kw_only=True)
    cfg_scale: int = field(default=7, kw_only=True)

    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict[str, Any]:
        prompt = ", ".join(prompts)

        request: dict[str, Any] = {"taskType": self.task_type}

        text_to_image_params: dict[str, Any] = {"text": prompt}
        if negative_prompts:
            text_to_image_params["negativeText"] = ", ".join(negative_prompts)

        image_generation_config: dict[str, Any] = {
            "numberOfImages": 1,
            "quality": self.quality,
            "width": image_width,
            "height": image_height,
            "cfgScale": self.cfg_scale,
        }
        if seed:
            image_generation_config["seed"] = seed

        request["textToImageParams"] = text_to_image_params
        request["imageGenerationConfig"] = image_generation_config

        return request

    def get_generated_image(self, response: dict[str, Any]) -> bytes:
        b64_image_data = response["images"][0]

        return base64.decodebytes(bytes(b64_image_data, "utf-8"))
