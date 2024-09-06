from __future__ import annotations

from attrs import define, field

from griptape.artifacts import CsvRowArtifact, ListArtifact
from griptape.drivers import BaseSqlDriver
from griptape.loaders import BaseLoader


@define
class SqlLoader(BaseLoader[str, list[BaseSqlDriver.RowResult], ListArtifact]):
    sql_driver: BaseSqlDriver = field(kw_only=True)

    def fetch(self, source: str) -> list[BaseSqlDriver.RowResult]:
        return self.sql_driver.execute_query(source) or []

    def parse(self, data: list[BaseSqlDriver.RowResult]) -> ListArtifact[CsvRowArtifact]:
        return ListArtifact([CsvRowArtifact(row.cells, meta={"row": row_num}) for row_num, row in enumerate(data)])
