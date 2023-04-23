from abc import ABC, abstractmethod
from griptape.memory import Memory


class MemoryDriver(ABC):
    @abstractmethod
    def store(self, memory: Memory) -> None:
        ...

    @abstractmethod
    def load(self) -> Memory:
        ...
