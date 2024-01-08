from attr import define
from abc import ABC, abstractmethod


@define
class BaseEmbeddingModelDriver(ABC):
    @abstractmethod
    def chunk_to_model_params(self, chunk: str) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: dict) -> list[float]:
        ...
