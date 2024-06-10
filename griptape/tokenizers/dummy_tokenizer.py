from __future__ import annotations
from attrs import define, field
from griptape.exceptions import DummyException
from griptape.tokenizers import BaseTokenizer
from griptape.common import BasePromptStackContent, PromptStackElement


@define
class DummyTokenizer(BaseTokenizer):
    model: None = field(init=False, default=None, kw_only=True)
    max_input_tokens: int = field(init=False, default=0, kw_only=True)
    max_output_tokens: int = field(init=False, default=0, kw_only=True)

    def try_count_tokens(self, text: str) -> int:
        raise DummyException(__class__.__name__, "count_tokens")

    def prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        raise DummyException(__class__.__name__, "prompt_stack_input_to_message")

    def prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> dict:
        raise DummyException(__class__.__name__, "prompt_stack_content_to_message_content")
