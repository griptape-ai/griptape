from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from anthropic import Anthropic


@define
class AnthropicImageQueryDriver(BaseImageQueryDriver):
    """Anthropic Image Query Driver.

    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    _client: Anthropic = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Anthropic:
        return import_optional_dependency("anthropic").Anthropic(api_key=self.api_key)

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        if self.max_tokens is None:
            raise TypeError("max_output_tokens can't be empty")

        response = self.client.messages.create(**self._base_params(query, images))
        content_blocks = response.content

        if len(content_blocks) < 1:
            raise ValueError("Response content is empty")

        text_content = content_blocks[0].text

        return TextArtifact(text_content)

    def _base_params(self, text_query: str, images: list[ImageArtifact]) -> dict:
        content = [self._construct_image_message(image) for image in images]
        content.append(self._construct_text_message(text_query))
        messages = self._construct_messages(content)
        return {"model": self.model, "messages": messages, "max_tokens": self.max_tokens}

    def _construct_image_message(self, image_data: ImageArtifact) -> dict:
        data = image_data.base64
        media_type = image_data.mime_type

        return {"source": {"data": data, "media_type": media_type, "type": "base64"}, "type": "image"}

    def _construct_text_message(self, query: str) -> dict:
        return {"text": query, "type": "text"}

    def _construct_messages(self, content: list) -> list:
        return [{"content": content, "role": "user"}]
