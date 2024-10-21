from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseSqlDriver
from griptape.loaders import BaseLoader


@define
class SqlLoader(BaseLoader[str, list[BaseSqlDriver.RowResult], ListArtifact[TextArtifact]]):
    sql_driver: BaseSqlDriver = field(kw_only=True)
    format_row: Callable[[dict], str] = field(
        default=lambda value: "\n".join(f"{key}: {val}" for key, val in value.items()), kw_only=True
    )

    def fetch(self, source: str) -> list[BaseSqlDriver.RowResult]:
        return self.sql_driver.execute_query(source) or []

    def parse(self, data: list[BaseSqlDriver.RowResult]) -> ListArtifact[TextArtifact]:
        return ListArtifact([TextArtifact(self.format_row(row.cells)) for row in data])
