from __future__ import annotations
from abc import ABC, abstractmethod
from attr import define, field, Factory
from griptape import utils


@define(frozen=True)
class BaseTokenizer(ABC):
    stop_sequences: list[str] = field(default=Factory(lambda: [utils.constants.RESPONSE_STOP_SEQUENCE]), kw_only=True)

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        ...

    def count_tokens_left(self, text: str | list) -> int:
        diff = self.max_tokens - self.count_tokens(text)

        if diff > 0:
            return diff
        else:
            return 0

    @abstractmethod
    def count_tokens(self, text: str | list) -> int:
        ...
