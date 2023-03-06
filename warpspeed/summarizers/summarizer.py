from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attrs import define

if TYPE_CHECKING:
    from warpspeed.steps import Step
    from warpspeed.memory import Memory


@define
class Summarizer(ABC):
    @abstractmethod
    def summarize(self, memory: Memory, steps: list[Step]) -> Optional[str]:
        ...
