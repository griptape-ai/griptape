from attr import define, field, Factory
from griptape.tokenizers import AnthropicTokenizer


@define(frozen=True)
class BedrockClaudeTokenizer(AnthropicTokenizer):
    DEFAULT_MODEL = 'anthropic.claude-v2'
    DEFAULT_MAX_TOKENS = 8192

    stop_sequences: list[str] = field(default=Factory(lambda: ["\n\nHuman:"]), kw_only=True)

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
