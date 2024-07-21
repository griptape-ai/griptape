from __future__ import annotations

from attrs import define, field

from griptape.tokenizers.base_tokenizer import BaseTokenizer


@define()
class AmazonBedrockTokenizer(BaseTokenizer):
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

    model: str = field(kw_only=True)
    characters_per_token: int = field(default=4, kw_only=True)

    def count_tokens(self, text: str) -> int:
        num_tokens = (len(text) + self.characters_per_token - 1) // self.characters_per_token

        return num_tokens
