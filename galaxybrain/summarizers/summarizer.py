from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attrs import define

if TYPE_CHECKING:
    from galaxybrain.workflows import Step, Memory


@define
class Summarizer(ABC):
    @abstractmethod
    def summarize(self, memory: Memory, steps: list[Step]) -> Optional[str]:
        pass
