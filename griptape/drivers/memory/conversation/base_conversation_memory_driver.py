from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from griptape.mixins import EventsMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


class BaseConversationMemoryDriver(EventsMixin, SerializableMixin, ABC):
    @abstractmethod
    def store(self, memory: BaseConversationMemory) -> None: ...

    @abstractmethod
    def load(self) -> Optional[BaseConversationMemory]: ...
