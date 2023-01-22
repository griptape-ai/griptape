from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from attrs import define

if TYPE_CHECKING:
    from galaxybrain.workflows import Workflow, Step


@define
class Summarizer(ABC):

    @abstractmethod
    def summarize(self, workflow: Workflow, steps: list[Step]) -> Optional[str]:
        pass
