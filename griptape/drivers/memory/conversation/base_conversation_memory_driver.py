from abc import ABC, abstractmethod
from griptape.memory.structure import ConversationMemory


class BaseConversationMemoryDriver(ABC):
    @abstractmethod
    def store(self, *args, **kwargs) -> None:
        ...

    @abstractmethod
    def load(self, *args, **kwargs) -> ConversationMemory:
        ...
