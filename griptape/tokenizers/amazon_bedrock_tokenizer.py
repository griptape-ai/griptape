from __future__ import annotations

from attrs import define, field

from griptape.common import BasePromptStackContent, ImagePromptStackContent, TextPromptStackContent
from griptape.common import PromptStackElement
from griptape.artifacts import TextArtifact
from griptape.tokenizers import SimpleTokenizer


@define()
class AmazonBedrockTokenizer(SimpleTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {
        "anthropic.claude-3": 200000,
        "anthropic.claude-v2:1": 200000,
        "anthropic.claude": 100000,
        "cohere.command-r": 128000,
        "cohere.embed": 512,
        "cohere.command": 4000,
        "cohere": 1024,
        "ai21": 8192,
        "meta-llama3": 8000,
        "meta-llama2": 4096,
        "mistral": 32000,
        "amazon": 4096,
    }
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {
        "anthropic.claude": 4096,
        "cohere": 4096,
        "ai21.j2": 8191,
        "meta": 2048,
        "amazon.titan-text-lite": 4096,
        "amazon.titan-text-express": 8192,
        "amazon.titan-text-premier": 3072,
        "amazon": 4096,
        "mistral": 8192,
    }

    characters_per_token: int = field(default=4, kw_only=True)

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        content = [self.prompt_stack_content_to_message_content(content) for content in prompt_input.content]

        if prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "source": {"type": "base64", "format": content.artifact.media_type, "bytes": content.artifact.value}
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def message_content_to_prompt_stack_content(self, message_content: dict) -> BasePromptStackContent:
        if "text " in message_content:
            return TextPromptStackContent(TextArtifact(message_content["text"]))
        else:
            raise ValueError(f"Unsupported message content type: {message_content['text']}")
