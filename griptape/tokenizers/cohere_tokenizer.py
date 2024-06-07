from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define, field
from griptape.tokenizers import BaseTokenizer
from griptape.common import PromptStack

if TYPE_CHECKING:
    from cohere import Client


@define()
class CohereTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"command-r": 128000, "command": 4096, "embed": 512}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"command": 4096, "embed": 512}

    client: Client = field(kw_only=True)

    def try_count_tokens(self, text: str) -> int:
        return len(self.client.tokenize(text=text, model=self.model).tokens)

    def prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        if prompt_input.is_system():
            return {"role": "SYSTEM", "text": prompt_input.content}
        elif prompt_input.is_user():
            return {"role": "USER", "text": prompt_input.content}
        else:
            return {"role": "ASSISTANT", "text": prompt_input.content}
