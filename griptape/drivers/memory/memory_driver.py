from abc import ABC, abstractmethod
from griptape.memory import PipelineMemory


class MemoryDriver(ABC):
    @abstractmethod
    def store(self, memory: PipelineMemory) -> None:
        ...

    @abstractmethod
    def load(self) -> PipelineMemory:
        ...
