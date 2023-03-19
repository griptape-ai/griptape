from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attrs import define

if TYPE_CHECKING:
    from warpspeed.memory import PipelineMemory, PipelineRun


@define
class Summarizer(ABC):
    @abstractmethod
    def summarize(self, memory: PipelineMemory, runs: list[PipelineRun]) -> Optional[str]:
        ...
