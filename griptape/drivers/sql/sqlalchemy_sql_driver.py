from typing import Optional
import sqlalchemy
from sqlalchemy.engine import Engine
from griptape.drivers import BaseSqlDriver
from sqlalchemy import create_engine, text, MetaData, Table
from attr import define, field


@define
class SqlalchemySqlDriver(BaseSqlDriver):
    engine_url: str = field(kw_only=True)
    engine: Engine = field(init=False)

    def __attrs_post_init__(self):
        self.engine = create_engine(self.engine_url)

    def execute_query(self, query: str) -> Optional[list[BaseSqlDriver.RowResult]]:
        with self.engine.begin() as con:
            results = con.execute(text(query))

            if results.returns_rows:
                return [BaseSqlDriver.RowResult(list(row)) for row in results]
            else:
                return None

    def execute_query_raw(self, query: str) -> Optional[str]:
        with self.engine.begin() as con:
            results = con.execute(text(query))

            if results.returns_rows:
                return str([row for row in results])
            else:
                return None

    def get_table_schema(self, table: str, schema: Optional[str] = None) -> Optional[str]:
        try:
            table = Table(
                table,
                MetaData(bind=self.engine),
                schema=schema,
                autoload=True,
                autoload_with=self.engine
            )
            return str([(c.name, c.type) for c in table.columns])
        except sqlalchemy.exc.NoSuchTableError:
            return None
