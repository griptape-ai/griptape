from attr import define
from griptape.tokenizers import AnthropicTokenizer


@define(frozen=True)
class BedrockClaudeTokenizer(AnthropicTokenizer):
    DEFAULT_MODEL = "anthropic.claude-v2:1"
    MODEL_PREFIXES_TO_MAX_TOKENS = {
        "anthropic.claude-3-sonnet-20240229-v1:0": 200000,
        "anthropic.claude-v2:1": 200000,
        "anthropic.claude": 100000,
    }
