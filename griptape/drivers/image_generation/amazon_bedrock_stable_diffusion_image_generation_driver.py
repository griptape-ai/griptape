import base64
import json
import random
from typing import Optional

import boto3
from attr import define, field, Factory
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver


@define
class AmazonBedrockStableDiffusionImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for Stable Diffusion provided by Amazon Bedrock.

    Attributes:
        session: Boto3 session.
        region_name: AWS region name.
        client: Bedrock runtime client.
        model_id: Bedrock model ID.
        image_width: Width of output images. Defaults to 512 and must be a multiple of 64.
        image_height: Height of output images. Defaults to 512 and must be a multiple of 64.
        cfg_scale: Stable Diffusion cfg_scale parameter.
        seed: Stable Diffusion seed parameter.
        steps: Stable Diffusion steps parameter.
        style_preset: Optional Stable Diffusion style preset name.
        clip_guidance_preset: Optional Stable Diffusion clip guidance preset name.
        sampler: Optional Stable Diffusion sampler name.

    Details on Stable Diffusion image generation parameters can be found here:
    https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/textToImage
    """

    session: boto3.Session = field(kw_only=True)
    region_name: str = field(kw_only=True)
    client: any = field(
        default=Factory(
            lambda self: self.session.client(service_name="bedrock-runtime", region_name=self.region_name),
            takes_self=True,
        )
    )
    model_id: str = field(default="stability.stable-diffusion-xl", kw_only=True)
    image_width: int = field(default=512, kw_only=True)
    image_height: int = field(default=512, kw_only=True)
    cfg_scale: int = field(default=7, kw_only=True)
    seed: int = field(default=0, kw_only=True)
    steps: int = field(default=60, kw_only=True)
    style_preset: Optional[str] = field(default=None, kw_only=True)
    clip_guidance_preset: Optional[str] = field(default=None, kw_only=True)
    sampler: Optional[str] = field(default=None, kw_only=True)

    def generate_image(self, prompts: list[str], negative_prompts: list[str] = None, **kwargs) -> ImageArtifact:
        if negative_prompts is None:
            negative_prompts = []

        request = {
            "text_prompts": [{"text": prompt, "weight": 1.0} for prompt in prompts]
            + [{"text": negative_prompt, "weight": -1.0} for negative_prompt in negative_prompts],
            "cfg_scale": self.cfg_scale,
            "seed": self.seed,
            "steps": self.steps,
            "style_preset": self.style_preset,
            "clip_guidance_preset": self.clip_guidance_preset,
            "sampler": self.sampler,
            "width": self.image_width,
        }

        response = self.client.invoke_model(
            body=json.dumps(request), modelId=self.model_id, accept="application/json", contentType="application/json"
        )

        response_body = json.loads(response.get("body").read())
        image_response = response_body["artifacts"][0]
        if image_response.get("finishReason") is not "SUCCESS":
            raise ValueError(f"Image generation failed: {image_response.get('finishReason')}")

        image_bytes = base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))

        return ImageArtifact(
            value=image_bytes,
            mime_type="image/png",
            width=self.image_width,
            height=self.image_width,
            model=self.model_id,
            prompt=", ".join(prompts),
        )
