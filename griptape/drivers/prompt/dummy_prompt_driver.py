from __future__ import annotations
from collections.abc import Iterator
from typing import Any

from attrs import Factory, define, field

from griptape.common import (
    BasePromptStackContent,
    PromptStack,
    PromptStackElement,
    DeltaPromptStackElement,
    BaseDeltaPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.exceptions import DummyException
from griptape.tokenizers import DummyTokenizer


@define
class DummyPromptDriver(BasePromptDriver):
    model: None = field(init=False, default=None, kw_only=True)
    tokenizer: DummyTokenizer = field(default=Factory(lambda: DummyTokenizer()), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        raise DummyException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        raise DummyException(__class__.__name__, "try_stream")

    def _prompt_stack_input_to_message(self, prompt_input: PromptStackElement) -> dict:
        raise DummyException(__class__.__name__, "_prompt_stack_input_to_message")

    def _prompt_stack_content_to_message_content(self, content: BasePromptStackContent) -> Any:
        raise DummyException(__class__.__name__, "_prompt_stack_content_to_message_content")

    def _message_content_to_prompt_stack_content(self, message_content: Any) -> BasePromptStackContent:
        raise DummyException(__class__.__name__, "_message_content_to_prompt_stack_content")
