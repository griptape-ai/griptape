from abc import ABC, abstractmethod
from attr import define


@define
class BaseModule(ABC):
    @abstractmethod
    def process(self, context: dict) -> dict:
        ...
