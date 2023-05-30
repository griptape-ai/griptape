from abc import ABC, abstractmethod
from griptape.memory.structure import Memory


class BaseMemoryDriver(ABC):
    @abstractmethod
    def store(self, memory: Memory) -> None:
        ...

    @abstractmethod
    def load(self) -> Memory:
        ...
