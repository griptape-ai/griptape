from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from galaxybrain.workflows import StepOutput


@define
class Driver(ABC):
    @abstractmethod
    def run(self, value: any) -> StepOutput:
        pass
