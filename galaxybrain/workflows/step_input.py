from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from attrs import define
from galaxybrain.workflows import StepArtifact

if TYPE_CHECKING:
    from galaxybrain.workflows import Workflow


@define
class StepInput(StepArtifact):
    @abstractmethod
    def to_string(self, workflow: Workflow) -> str:
        pass
