from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from attr import define


@define
class BaseSqlDriver(ABC):
    @dataclass
    class RowResult:
        cells: list[any]

    @abstractmethod
    def execute_query(self, query: str) -> Optional[list[RowResult]]:
        ...

    @abstractmethod
    def execute_query_raw(self, query: str) -> Optional[str]:
        ...
