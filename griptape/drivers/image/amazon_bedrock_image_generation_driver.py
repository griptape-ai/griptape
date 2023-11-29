from __future__ import annotations

import json
from typing import Optional, TYPE_CHECKING, Any

from attr import define, field, Factory

from griptape.artifacts import ImageArtifact
from griptape.drivers.image.base_multi_model_combined_generation_driver import BaseMultiModelCombinedGenerationDriver
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseMultiModelImageToImageGenerationDriver, BaseMultiModelTextToImageGenerationDriver

if TYPE_CHECKING:
    import boto3


@define
class AmazonBedrockImageGenerationDriver(BaseMultiModelCombinedGenerationDriver):
    """Driver for image generation models provided by Amazon Bedrock.

    Attributes:
        model: Bedrock model ID.
        session: boto3 session.
        bedrock_client: Bedrock runtime client.
        image_width: Width of output images. Defaults to 512 and must be a multiple of 64.
        image_height: Height of output images. Defaults to 512 and must be a multiple of 64.
        seed: Optionally provide a consistent seed to generation requests, increasing consistency in output.
        text_to_image_generation_model_driver: Image Generation Model Driver to use.

    Details on Stable Diffusion image generation parameters can be found here:
    https://platform.stability.ai/docs/api-reference#tag/v1generation/operation/textToImage
    """

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client(service_name="bedrock-runtime"), takes_self=True)
    )
    image_width: int = field(default=512, kw_only=True)
    image_height: int = field(default=512, kw_only=True)
    seed: int | None = field(default=None, kw_only=True)

    def try_generate_image(self, prompts: list[str], negative_prompts: list[str] | None = None) -> ImageArtifact:
        request = self.image_generation_model_driver.text_to_image_request_parameters(
            prompts, self.image_width, self.image_height, negative_prompts=negative_prompts, seed=self.seed
        )

        response = self.bedrock_client.invoke_model(
            body=json.dumps(request), modelId=self.model, accept="application/json", contentType="application/json"
        )

        response_body = json.loads(response.get("body").read())

        try:
            image_bytes = self.image_generation_model_driver.get_generated_image(response_body)
        except Exception as e:
            raise ValueError(f"Text to image generation failed: {e}")

        return ImageArtifact(
            prompt=", ".join(prompts),
            value=image_bytes,
            mime_type="image/png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
        )

    def try_image_to_image_generation(
        self,
        image: ImageArtifact,
        prompts: list[str],
        mask_image: Optional[ImageArtifact] = None,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        request = self.image_generation_model_driver.image_to_image_request_parameters(
            prompts, image=image, mask_image=mask_image, negative_prompts=negative_prompts, seed=self.seed
        )

        response = self.bedrock_client.invoke_model(
            body=json.dumps(request), modelId=self.model, accept="application/json", contentType="application/json"
        )

        response_body = json.loads(response.get("body").read())

        try:
            image_bytes = self.image_generation_model_driver.get_generated_image(response_body)
        except Exception as e:
            raise ValueError(f"Image to image generation failed: {e}")

        return ImageArtifact(
            prompt=", ".join(prompts),
            value=image_bytes,
            mime_type="image/png",
            width=image.width,
            height=image.height,
            model=self.model,
        )
