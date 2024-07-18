from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseSqlDriver
from griptape.utils import import_optional_dependency

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

    def execute_query(self, query: str) -> Optional[list[BaseSqlDriver.RowResult]]:
        rows = self.execute_query_raw(query)

        if rows:
            return [BaseSqlDriver.RowResult(row) for row in rows]
        else:
            return None

    def execute_query_raw(self, query: str) -> Optional[list[dict[str, Optional[Any]]]]:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        with self.engine.connect() as con:
            results = con.execute(sqlalchemy.text(query))

            if results is not None:
                if results.returns_rows:
                    return [dict(result._mapping) for result in results]
                else:
                    con.commit()
            else:
                raise ValueError("No result found")

    def get_table_schema(self, table_name: str, schema: Optional[str] = None) -> Optional[str]:
        sqlalchemy = import_optional_dependency("sqlalchemy")
        sqlalchemy_exc = import_optional_dependency("sqlalchemy.exc")

        try:
            table = sqlalchemy.Table(table_name, sqlalchemy.MetaData(), schema=schema, autoload_with=self.engine)
            return str([(c.name, c.type) for c in table.columns])
        except sqlalchemy_exc.NoSuchTableError:
            return None
