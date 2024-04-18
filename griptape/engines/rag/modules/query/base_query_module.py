from abc import ABC, abstractmethod

from attr import define


@define(kw_only=True)
class BaseQueryModule(ABC):
    @abstractmethod
    def run(self, query: str) -> str:
        ...
