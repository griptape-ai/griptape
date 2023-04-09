from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attr import define, field, Factory

if TYPE_CHECKING:
    from skatepark.memory import PipelineMemory, PipelineRun


@define
class Summarizer(ABC):
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @abstractmethod
    def summarize(self, memory: PipelineMemory, runs: list[PipelineRun]) -> Optional[str]:
        ...
