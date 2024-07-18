from __future__ import annotations

from attrs import define

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryModelDriver


@define
class BedrockClaudeImageQueryModelDriver(BaseImageQueryModelDriver):
    ANTHROPIC_VERSION = "bedrock-2023-05-31"  # static string for AWS: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html#api-inference-examples-claude-multimodal-code-example

    def image_query_request_parameters(self, query: str, images: list[ImageArtifact], max_tokens: int) -> dict:
        content = [self._construct_image_message(image) for image in images]
        content.append(self._construct_text_message(query))
        messages = self._construct_messages(content)
        input_params = {"messages": messages, "anthropic_version": self.ANTHROPIC_VERSION, "max_tokens": max_tokens}

        return input_params

    def process_output(self, output: dict) -> TextArtifact:
        content_blocks = output["content"]
        if len(content_blocks) < 1:
            raise ValueError("Response content is empty")

        text_content = content_blocks[0]["text"]

        return TextArtifact(text_content)

    def _construct_image_message(self, image_data: ImageArtifact) -> dict:
        data = image_data.base64
        media_type = image_data.mime_type

        return {"source": {"data": data, "media_type": media_type, "type": "base64"}, "type": "image"}

    def _construct_text_message(self, query: str) -> dict:
        return {"text": query, "type": "text"}

    def _construct_messages(self, content: list) -> list:
        return [{"content": content, "role": "user"}]
