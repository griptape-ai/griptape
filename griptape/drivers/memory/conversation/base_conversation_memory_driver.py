from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


class BaseConversationMemoryDriver(ABC):
    @abstractmethod
    def store(self, memory: BaseConversationMemory) -> None:
        ...

    @abstractmethod
    def load(self) -> Optional[BaseConversationMemory]:
        ...
