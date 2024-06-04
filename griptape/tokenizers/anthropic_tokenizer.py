from __future__ import annotations
from attrs import define, field, Factory
from typing import TYPE_CHECKING
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer
from griptape.utils import PromptStack

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

    def prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        content = prompt_input.content

        if prompt_input.is_system():
            return {"role": "system", "content": content}
        elif prompt_input.is_assistant():
            return {"role": "assistant", "content": content}
        else:
            return {"role": "user", "content": content}
