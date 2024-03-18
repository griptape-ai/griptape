from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field, Factory
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.tokenizers import AnthropicTokenizer
from griptape.utils import import_optional_dependency
import base64

if TYPE_CHECKING:
    from anthropic import Anthropic


@define
class AnthropicImageQueryDriver(BaseImageQueryDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
        tokenizer: Custom `AnthropicTokenizer`.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model: str = field(default="claude-3-sonnet-20240229", kw_only=True, metadata={"serializable": True})
    client: Anthropic = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    tokenizer: AnthropicTokenizer = field(
        default=Factory(
            lambda self: AnthropicTokenizer(model=self.model, max_tokens=4096), takes_self=True
        ),  # TODO: Fix tokens after Collin's change goes in
        kw_only=True,
    )

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        content = []
        for image in images:
            content.append(self._construct_image_message(image))

        content.append(self._construct_text_message(query))
        messages = self._construct_messages(content)

        response = self.client.messages.create(
            model=self.model, max_tokens=self.tokenizer.max_tokens, messages=messages
        )

        text_content = response.content

        return TextArtifact(text_content)

    def _construct_image_message(self, image_data: ImageArtifact) -> dict:
        data = base64.b64encode(image_data.value).decode("utf-8")
        type = image_data.mime_type

        return {"source": {"data": data, "media_type": type, "type": "base64"}, "type": "image"}


    def _construct_text_message(self, query: str) -> dict:
        return {"text": query, "type": "text"}

    def _construct_messages(self, content: list) -> list:
        return [{"content": content, "role": "user"}]
