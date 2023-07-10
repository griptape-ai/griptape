from typing import Optional
from griptape.drivers import BaseSqlDriver
from attr import Factory, define, field
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoSuchTableError


@define
class SnowflakeSqlDriver(BaseSqlDriver):
    engine_url: str = field(kw_only=True)
    create_engine_params: dict = field(factory=dict, kw_only=True)
    engine: Engine = field(
        default=Factory(
            lambda self: create_engine(self.engine_url, **self.create_engine_params),
            takes_self=True,
        ),
        kw_only=True,
    )

    @engine_url.validator
    def validate_engine_url(self, _, engine_url: str) -> None:
        if not engine_url.startswith("snowflake://"):
            raise ValueError("Provide a Snowflake engine URL")

    def execute_query(self, query: str) -> Optional[list[BaseSqlDriver.RowResult]]:
        rows = self.execute_query_raw(query)

        if rows:
            return [BaseSqlDriver.RowResult(row) for row in rows]
        else:
            return None

    def execute_query_raw(self, query: str) -> Optional[list[dict[str, any]]]:
        results = None
        with self.engine.connect() as con:
            try:
                results = con.execute(text(query))

                if results.returns_rows:
                    results = [
                        {column: value for column, value in result.items()}
                        for result in results
                    ]
            finally:
                con.close()
        self.engine.dispose()
        return results

    def get_table_schema(
        self, table: str, schema: Optional[str] = None
    ) -> Optional[str]:
        try:
            metadata_obj = MetaData()
            metadata_obj.reflect(bind=self.engine)
            table = Table(
                table,
                metadata_obj,
                schema=schema,
                autoload=True,
                autoload_with=self.engine,
            )
            return str([(c.name, c.type) for c in table.columns])
        except NoSuchTableError:
            return None
