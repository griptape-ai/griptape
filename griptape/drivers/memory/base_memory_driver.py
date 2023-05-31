from abc import ABC, abstractmethod
from griptape.memory.structure import ConversationMemory


class BaseMemoryDriver(ABC):
    @abstractmethod
    def store(self, memory: ConversationMemory) -> None:
        ...

    @abstractmethod
    def load(self) -> ConversationMemory:
        ...
