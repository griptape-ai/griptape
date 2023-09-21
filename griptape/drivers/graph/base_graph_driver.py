from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from attr import define

@define
class BaseGraphDriver(ABC):
    @dataclass
    class NodeResult:
        properties: dict[str, any]

    @abstractmethod
    def execute_query(self, query: str) -> Optional[list[NodeResult]]:
        ...

    # @abstractmethod
    # def execute_query_raw(self, query: str) -> Optional[list[dict[str, any]]]:
    #     ...
    #
    # @abstractmethod
    # def get_schema(self) -> str:
    #     ...