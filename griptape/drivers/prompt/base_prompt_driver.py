from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.tokenizers import BaseTokenizer
from griptape.events import StartPromptEvent, FinishPromptEvent

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.structures import Structure


@define
class BasePromptDriver(ABC):
    prompt_prefix: str = field(default="", kw_only=True)
    prompt_suffix: str = field(default="", kw_only=True)
    max_retries: int = field(default=8, kw_only=True)
    retry_delay: float = field(default=1, kw_only=True)
    temperature: float = field(default=0.1, kw_only=True)
    model: str
    tokenizer: BaseTokenizer
    structure: Optional[Structure] = field(default=None, kw_only=True)

    def run(self, value: str) -> TextArtifact:
        for attempt in range(0, self.max_retries + 1):
            try:
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
            except Exception as e:
                logging.error(f"PromptDriver.run attempt {attempt} failed: {e}\nRetrying in {self.retry_delay} seconds")

                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise e

    def full_prompt(self, value: str) -> str:
        return f"{self.prompt_prefix}{value}{self.prompt_suffix}"

    @abstractmethod
    def try_run(self, value: str) -> TextArtifact:
        ...
