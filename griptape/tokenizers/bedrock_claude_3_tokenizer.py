from attr import define, field, Factory
from griptape.tokenizers import BedrockClaudeTokenizer
from griptape import utils


@define(frozen=True)
class BedrockClaude3Tokenizer(BedrockClaudeTokenizer):
    DEFAULT_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
    stop_sequences: list[str] = field(
        default=Factory(lambda: [utils.constants.RESPONSE_STOP_SEQUENCE, "</function_calls>"]), kw_only=True
    )
