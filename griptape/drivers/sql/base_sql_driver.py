from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from attrs import define


@define
class BaseSqlDriver(ABC):
    @dataclass
    class RowResult:
        cells: dict[str, Any]

    @abstractmethod
    def execute_query(self, query: str) -> list[RowResult] | None:
        pass

    @abstractmethod
    def execute_query_raw(self, query: str) -> list[dict[str, Any]] | None:
        pass

    @abstractmethod
    def get_table_schema(self, table_name: str, schema: str | None = None) -> str | None:
        pass
