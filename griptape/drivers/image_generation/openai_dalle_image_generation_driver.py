import os
import openai
from typing import Optional
import requests
from attr import field, Factory, define
from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver


@define
class OpenAiDalleImageGenerationDriver(BaseImageGenerationDriver):
    """Driver for OpenAI DALLE image generation API.

    Attributes:
        api_type: OpenAI API type. Defaults to 'davinci'.
        api_version: API version. Defaults to '2020-12-15'.
        api_base: API URL.
        api_key: OpenAI API key.
        organization: OpenAI organization ID.
        requests_session: Optionally provide custom `requests.Session`.
        image_size: Image size. Defaults to '512x512'.
    """

    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    requests_session: requests.Session = field(default=Factory(lambda: requests.Session()), kw_only=True)

    # Dalle2 accepts these three image sizes.
    IMAGE_SIZE_256: str = "256x256"
    IMAGE_SIZE_512: str = "512x512"
    IMAGE_SIZE_1024: str = "1024x1024"

    image_size: str = field(default=IMAGE_SIZE_512, kw_only=True)

    image_size_ints = {IMAGE_SIZE_256: 256, IMAGE_SIZE_512: 512, IMAGE_SIZE_1024: 1024}

    @image_size.validator
    def _validate_image_size(self, _, image_size: str):
        if image_size not in self.image_size_ints:
            raise ValueError(f"image_size must be one of {self.image_size_ints.keys()}")

    def generate_image(self, prompts: list[str], **kwargs) -> ImageArtifact:
        prompt = ", ".join(prompts)
        image_url = self._make_request(prompt=prompt)
        image_data = self._download_image(url=image_url)

        dim = self.image_size_ints[self.image_size]
        return ImageArtifact(
            value=image_data, mime_type="image/png", width=dim, height=dim, model="openai/dalle2", prompt=prompt
        )

    def _make_request(self, prompt: str) -> str:
        response = openai.Image.create(
            organization=self.organization,
            api_version=self.api_version,
            api_base=self.api_base,
            api_type=self.api_type,
            api_key=self.api_key,
            prompt=prompt,
            size=self.image_size,
            n=1,
        )

        return response["data"][0]["url"]

    def _download_image(self, url: str) -> bytes:
        response = self.requests_session.get(url=url)

        return response.content
