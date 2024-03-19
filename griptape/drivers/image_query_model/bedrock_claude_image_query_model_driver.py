from __future__ import annotations
import base64
import json
from typing import Any, Optional
from attr import field, define
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryModelDriver


@define
class BedrockClaudeImageQueryModelDriver(BaseImageQueryModelDriver):
    """
    Attributes:
        max_output_tokens: Max output tokens to return.
    """

    max_output_tokens: Optional[int] = field(default=4096, kw_only=True, metadata={"serializable": True})

    def construct_query_image_request_parameters(self, query: str, images: list[ImageArtifact]) -> dict:
        content = []
        for image in images:
            content.append(self._construct_image_message(image))

        content.append(self._construct_text_message(query))
        messages = self._construct_messages(content)

        input_params = {
            "max_tokens": self.max_output_tokens,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
        }

        return input_params

    def process_output(self, output: dict) -> TextArtifact:
        content = output["content"]
        return TextArtifact(content)

    def _construct_image_message(self, image_data: ImageArtifact) -> dict:
        data = base64.b64encode(image_data.value).decode("utf-8")
        type = image_data.mime_type

        return {"source": {"data": data, "media_type": type, "type": "base64"}, "type": "image"}

    def _construct_text_message(self, query: str) -> dict:
        return {"text": query, "type": "text"}

    def _construct_messages(self, content: list) -> list:
        return [{"content": content, "role": "user"}]
