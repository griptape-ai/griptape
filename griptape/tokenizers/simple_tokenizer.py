from __future__ import annotations
from attrs import define, field
from griptape.tokenizers import BaseTokenizer
from griptape.common import BasePromptStackContent


@define()
class SimpleTokenizer(BaseTokenizer):
    characters_per_token: int = field(kw_only=True)

    def try_count_tokens(self, text: str) -> int:
        num_tokens = (len(text) + self.characters_per_token - 1) // self.characters_per_token

        return num_tokens

    def prompt_stack_input_to_message_input(self, content: BasePromptStackContent) -> dict:
        raise NotImplementedError("SimpleTokenizer does not support prompt stack content to message conversion.")

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict | list[dict]:
        raise NotImplementedError("SimpleTokenizer does not support prompt stack content to message conversion.")
