from __future__ import annotations
import base64
import json
from typing import Optional, TYPE_CHECKING, Any
from attr import define, field, Factory
from griptape.artifacts import ImageArtifact
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseImageGenerationDriver

if TYPE_CHECKING:
    import boto3


@define
class AmazonBedrockStableDiffusionImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for Stable Diffusion provided by Amazon Bedrock.

    Attributes:
        model: Bedrock model ID.
        session: boto3 session.
        bedrock_client: Bedrock runtime client.
        image_width: Width of output images. Defaults to 512 and must be a multiple of 64.
        image_height: Height of output images. Defaults to 512 and must be a multiple of 64.
        cfg_scale: Stable Diffusion cfg_scale parameter.
        style_preset: Optional Stable Diffusion style preset name.
        clip_guidance_preset: Optional Stable Diffusion clip guidance preset name.
        sampler: Optional Stable Diffusion sampler name.
        steps: Optionally specify the number of inference steps to run for each image generation request, [10, 50].
        seed: Optionally provide a consistent seed to generation requests, increasing consistency in output.

    Details on Stable Diffusion image generation parameters can be found here:
    https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/textToImage
    """

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client(service_name="bedrock-runtime"), takes_self=True)
    )
    image_width: int = field(default=512, kw_only=True)
    image_height: int = field(default=512, kw_only=True)
    cfg_scale: int = field(default=7, kw_only=True)
    style_preset: Optional[str] = field(default=None, kw_only=True)
    clip_guidance_preset: Optional[str] = field(default=None, kw_only=True)
    sampler: Optional[str] = field(default=None, kw_only=True)
    steps: Optional[int] = field(default=None, kw_only=True)
    seed: Optional[int] = field(default=None, kw_only=True)

    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
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
            "width": self.image_width,
            "height": self.image_height,
        }

        if self.steps is not None:
            request["steps"] = self.steps

        if self.seed is not None:
            request["seed"] = self.seed

        response = self.bedrock_client.invoke_model(
            body=json.dumps(request), modelId=self.model, accept="application/json", contentType="application/json"
        )

        response_body = json.loads(response.get("body").read())
        image_response = response_body["artifacts"][0]
        if image_response.get("finishReason") != "SUCCESS":
            raise ValueError(f"Image generation failed: {image_response.get('finishReason')}")

        image_bytes = base64.decodebytes(bytes(image_response.get("base64"), "utf-8"))

        return ImageArtifact(
            prompt=", ".join(prompts),
            value=image_bytes,
            mime_type="image/png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
        )
