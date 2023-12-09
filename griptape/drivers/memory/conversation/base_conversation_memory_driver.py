from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from griptape.memory.structure import ConversationMemory


class BaseConversationMemoryDriver(ABC):
    @abstractmethod
    def store(self, *args, **kwargs) -> None:
        ...

    @abstractmethod
    def load(self, *args, **kwargs) -> ConversationMemory | None:
        ...
