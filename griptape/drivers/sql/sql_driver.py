from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Any
from griptape.drivers import BaseSqlDriver
from griptape.utils import import_optional_dependency
from attr import define, field


if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


@define
class SqlDriver(BaseSqlDriver):
    engine_url: str = field(kw_only=True)
    create_engine_params: dict = field(factory=dict, kw_only=True)
    engine: Engine = field(init=False)

    def __attrs_post_init__(self) -> None:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        self.engine = sqlalchemy.create_engine(self.engine_url, **self.create_engine_params)

    def execute_query(self, query: str) -> list[BaseSqlDriver.RowResult] | None:
        rows = self.execute_query_raw(query)

        if rows:
            return [BaseSqlDriver.RowResult(row) for row in rows]
        else:
            return None

    def execute_query_raw(self, query: str) -> list[dict[str, Any]] | None:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        with self.engine.begin() as con:
            results = con.execute(sqlalchemy.text(query))

            if results.returns_rows:
                return [{column: value for column, value in result.items()} for result in results]
            else:
                return None

    def get_table_schema(self, table: str, schema: str | None = None) -> str | None:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        try:
            table = sqlalchemy.Table(
                table, sqlalchemy.MetaData(bind=self.engine), schema=schema, autoload=True, autoload_with=self.engine
            )
            return str([(c.name, c.type) for c in table.columns])
        except sqlalchemy.exc.NoSuchTableError:
            return None
