from __future__ import annotations
from attrs import define, field, Factory
from typing import TYPE_CHECKING
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer
from griptape.artifacts import TextArtifact
from griptape.common import BasePromptStackContent, ImagePromptStackContent, TextPromptStackContent, PromptStackElement

if TYPE_CHECKING:
    from anthropic import Anthropic


@define()
class AnthropicTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"claude-3": 200000, "claude-2.1": 200000, "claude": 100000}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"claude": 4096}

    client: Anthropic = field(
        default=Factory(lambda: import_optional_dependency("anthropic").Anthropic()), kw_only=True
    )

    def try_count_tokens(self, text: str) -> int:
        return self.client.count_tokens(text)

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        message_content = [self.prompt_stack_content_to_message_content(content) for content in prompt_input.content]

        if prompt_input.is_system():
            return {"role": "system", "content": message_content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": message_content}
        else:
            return {"role": "user", "content": message_content}

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": content.artifact.media_type,
                    "data": content.artifact.base64,
                },
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def message_content_to_prompt_stack_content(self, message_content: dict) -> BasePromptStackContent:
        if message_content["type"] == "text":
            return TextPromptStackContent(TextArtifact(message_content["text"]))
        else:
            raise ValueError(f"Unsupported message content type: {message_content['type']}")
