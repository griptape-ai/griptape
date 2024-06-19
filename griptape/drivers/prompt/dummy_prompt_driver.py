from __future__ import annotations
from collections.abc import Iterator

from attrs import Factory, define, field

from griptape.common import PromptStack, PromptStackMessage, DeltaPromptStackMessage, BaseDeltaPromptStackContent
from griptape.drivers import BasePromptDriver
from griptape.exceptions import DummyException
from griptape.tokenizers import DummyTokenizer


@define
class DummyPromptDriver(BasePromptDriver):
    model: None = field(init=False, default=None, kw_only=True)
    tokenizer: DummyTokenizer = field(default=Factory(lambda: DummyTokenizer()), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        raise DummyException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        raise DummyException(__class__.__name__, "try_stream")
