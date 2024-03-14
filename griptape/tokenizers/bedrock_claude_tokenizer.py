from attr import define
from griptape.tokenizers import AnthropicTokenizer


@define()
class BedrockClaudeTokenizer(AnthropicTokenizer):
    MODEL_PREFIXES_TO_MAX_TOKENS = {"anthropic.claude-v2:1": 200000, "anthropic.claude": 100000}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"anthropic.claude": 4096}
