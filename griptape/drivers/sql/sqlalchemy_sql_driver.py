from typing import Optional
from sqlalchemy.engine import Engine
from griptape.drivers import BaseSqlDriver
from sqlalchemy import create_engine, text, MetaData
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

    def get_schema(self, table: str) -> Optional[str]:
        meta_data = MetaData(bind=self.engine)

        meta_data.reflect()

        if meta_data.tables.get(table) is None:
            return None
        else:
            return str([(c.name, c.type) for c in meta_data.tables[table].columns])
