import base64
from typing import Optional

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
    ) -> dict:
        prompt = ", ".join(prompts)

        request = {
            "taskType": self.task_type,
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

    def get_generated_image(self, response: dict) -> bytes:
        b64_image_data = response["images"][0]

        return base64.decodebytes(bytes(b64_image_data, "utf-8"))
