from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from attrs import define, field, Factory
from warpspeed.utils import Tokenizer

if TYPE_CHECKING:
    from warpspeed.artifacts import TextOutput


@define
class PromptDriver(ABC):
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    tokenizer: Tokenizer

    @abstractmethod
    def run(self, **kwargs) -> TextOutput:
        ...
