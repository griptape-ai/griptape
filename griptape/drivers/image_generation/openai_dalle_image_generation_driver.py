import base64
import openai
from typing import Optional
from attr import field, Factory, define
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver


@define
class OpenAiDalleImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for OpenAI DALLE image generation API.

    Attributes:
        model: OpenAI DALLE model, for example 'dall-e-2' or 'dall-e-3'.
        api_type: OpenAI API type, for example 'open_ai' or 'azure'.
        api_version: API version.
        base_url: API URL.
        api_key: OpenAI API key.
        organization: OpenAI organization ID.
        style: Optional and only supported for dall-e-3, can be either 'vivid' or 'natural'.
        quality: Optional and only supported for dall-e-3. Accepts 'standard', 'hd'.
        image_width: The width of the generated image.
        image_height: The height of the generated image.

    Image dimensions must be one of the following, depending on the requested model:
    dall-e-2: [256x256, 512x512, 1024x1024]
    dall-e-3: [1024x1024, 1024x1792, 1792x1024]
    """

    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    base_url: str = field(default=None, kw_only=True)
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )
    style: Optional[str] = field(default=None, kw_only=True)
    quality: Optional[str] = field(default=None, kw_only=True)
    image_width: int = field(default=512, kw_only=True)
    image_height: int = field(default=512, kw_only=True)

    def generate_image(self, prompts: list[str], **kwargs) -> ImageArtifact:
        prompt = ", ".join(prompts)

        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=f"{self.image_width}x{self.image_height}",
            response_format="b64_json",
            n=1,
            style=self.style,
            quality=self.quality,
        )

        image_data = base64.b64decode(response.data[0].b64_json)

        return ImageArtifact(
            value=image_data,
            mime_type="image/png",
            width=self.image_width,
            height=self.image_height,
            model=self.model,
            prompt=prompt,
        )
