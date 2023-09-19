from attr import define, field
from griptape.tokenizers import AnthropicTokenizer


@define(frozen=True)
class BedrockClaudeTokenizer(AnthropicTokenizer):
    DEFAULT_MODEL = 'anthropic.claude-v2'
    DEFAULT_MAX_TOKENS = 8192

    stop_sequences: list[str] = field(factory=list, kw_only=True)

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
