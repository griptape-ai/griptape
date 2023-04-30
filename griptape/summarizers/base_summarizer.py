from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from attr import define, field, Factory

if TYPE_CHECKING:
    from griptape.memory import Run


@define
class BaseSummarizer(ABC):
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @abstractmethod
    def summarize_runs(self, previous_summary: str, runs: list[Run]) -> str:
        ...

    @abstractmethod
    def summarize_text(self, text: str) -> str:
        ...
