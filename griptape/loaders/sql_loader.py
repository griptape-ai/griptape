from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from attrs import define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.loaders import BaseLoader

if TYPE_CHECKING:
    from griptape.drivers import BaseSqlDriver


@define
class SqlLoader(BaseLoader):
    sql_driver: BaseSqlDriver = field(kw_only=True)

    def load(self, source: Any, *args, **kwargs) -> ListArtifact:
        return cast(ListArtifact, super().load(source, *args, **kwargs))

    def fetch(self, source: str, *args, **kwargs) -> list[BaseSqlDriver.RowResult]:
        return self.sql_driver.execute_query(source) or []

    def parse(self, source: list[BaseSqlDriver.RowResult], *args, **kwargs) -> ListArtifact:
        return ListArtifact([TextArtifact(row.cells, meta={"row": row_num}) for row_num, row in enumerate(source)])
