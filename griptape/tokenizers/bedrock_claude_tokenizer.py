from attr import define, field, Factory
from griptape.tokenizers import BaseTokenizer, AnthropicTokenizer


@define(frozen=True)
class BedrockClaudeTokenizer(AnthropicTokenizer):
    DEFAULT_MODEL = 'anthropic.claude-v2'
    DEFAULT_MAX_TOKENS = 8192

    stop_sequences: list[str] = field(
        default=Factory(lambda: BaseTokenizer.DEFAULT_STOP_SEQUENCES + ["\n\nHuman:"]), kw_only=True
    )
