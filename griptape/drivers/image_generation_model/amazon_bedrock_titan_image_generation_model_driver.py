from typing import Optional
from attr import field
from griptape.drivers import BaseImageGenerationModelDriver


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

        if negative_prompts:
            negative_prompt = ", ".join(negative_prompts)
        else:
            negative_prompt = ""

        request = {
            "taskType": self.task_type,
            "textToImageParams": {"text": prompt, "negativeText": negative_prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": self.quality,
                "width": image_width,
                "height": image_height,
                "cfgScale": self.cfg_scale,
                "seed": seed,
            },
        }

        return request
