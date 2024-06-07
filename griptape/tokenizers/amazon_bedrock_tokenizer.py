from __future__ import annotations
from attrs import define, field
from griptape.utils import PromptStack
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

    def prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        content = [{"text": prompt_input.content}]

        if prompt_input.is_system():
            return {"text": prompt_input.content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}
