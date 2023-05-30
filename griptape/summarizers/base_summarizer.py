from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from attr import define

if TYPE_CHECKING:
    from griptape.memory.structure import Run


@define
class BaseSummarizer(ABC):
    @abstractmethod
    def summarize_runs(self, previous_summary: str, runs: list[Run]) -> str:
        ...

    @abstractmethod
    def summarize_text(self, text: str) -> str:
        ...
