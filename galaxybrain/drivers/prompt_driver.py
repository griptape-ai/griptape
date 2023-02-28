from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from attrs import define
from galaxybrain.utils import Tokenizer

if TYPE_CHECKING:
    from galaxybrain.workflows import StepOutput


@define
class PromptDriver(ABC):
    tokenizer: Tokenizer

    @abstractmethod
    def run(self, **kwargs) -> StepOutput:
        pass
