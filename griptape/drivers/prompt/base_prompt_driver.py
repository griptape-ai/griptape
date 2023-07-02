from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.core import ExponentialBackoffMixin
from griptape.events import StartPromptEvent, FinishPromptEvent
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.structures import Structure


@define
class BasePromptDriver(ExponentialBackoffMixin, ABC):
    prompt_prefix: str = field(default="", kw_only=True)
    prompt_suffix: str = field(default="", kw_only=True)
    temperature: float = field(default=0.1, kw_only=True)
    structure: Optional[Structure] = field(default=None, kw_only=True)

    model: str
    tokenizer: BaseTokenizer

    def run(self, value: str) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                if self.structure:
                    self.structure.publish_event(
                        StartPromptEvent(
                            token_count=self.tokenizer.token_count(value)
                        )
                    )

                result = self.try_run(self.full_prompt(value))

                if self.structure:
                    self.structure.publish_event(
                        FinishPromptEvent(
                            token_count=result.token_count(self.tokenizer)
                        )
                    )

                return result

    def full_prompt(self, value: str) -> str:
        return f"{self.prompt_prefix}{value}{self.prompt_suffix}"

    @abstractmethod
    def try_run(self, value: str) -> TextArtifact:
        ...
