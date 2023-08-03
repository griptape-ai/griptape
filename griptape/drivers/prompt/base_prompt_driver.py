from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.core import ExponentialBackoffMixin, PromptStack
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.structures import Structure


@define
class BasePromptDriver(ExponentialBackoffMixin, ABC):
    temperature: float = field(default=0.1, kw_only=True)
    max_tokens: Optional[int] = field(default=None, kw_only=True)
    structure: Optional[Structure] = field(default=None, kw_only=True)

    model: str
    tokenizer: BaseTokenizer

    def run(self, prompt_stack: PromptStack) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                result = self.try_run(prompt_stack)

                return result

    @abstractmethod
    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        ...
