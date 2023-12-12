from __future__ import annotations
from typing import Callable, Optional, TYPE_CHECKING, Any
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseSqlDriver
from attr import Factory, define, field

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from snowflake.connector import SnowflakeConnection


@define
class SnowflakeSqlDriver(BaseSqlDriver):
    connection_func: Callable[[], SnowflakeConnection] = field(kw_only=True)
    engine: Engine = field(
        default=Factory(
            # Creator bypasses the URL param
            # https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine.params.creator
            lambda self: import_optional_dependency("sqlalchemy").create_engine(
                "snowflake://not@used/db", creator=self.connection_func
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    @connection_func.validator
    def validate_connection_func(self, _, connection_func: Callable[[], SnowflakeConnection]) -> None:
        snowflake_connection = connection_func()
        snowflake = import_optional_dependency("snowflake")

        if not isinstance(snowflake_connection, snowflake.connector.SnowflakeConnection):
            raise ValueError("The connection_func must return a SnowflakeConnection")
        if not snowflake_connection.schema or not snowflake_connection.database:
            raise ValueError("Provide a schema and database for the Snowflake connection")

    @engine.validator
    def validate_engine_url(self, _, engine: Engine) -> None:
        if not engine.url.render_as_string().startswith("snowflake://"):
            raise ValueError("Provide a Snowflake connection")

    def execute_query(self, query: str) -> list[BaseSqlDriver.RowResult] | None:
        rows = self.execute_query_raw(query)

        if rows:
            return [BaseSqlDriver.RowResult(row) for row in rows]
        else:
            return None

    def execute_query_raw(self, query: str) -> list[dict[str, Any]] | None:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        with self.engine.connect() as con:
            results = con.execute(sqlalchemy.text(query))

            if results.returns_rows:
                return [{column: value for column, value in result.items()} for result in results]
            else:
                return None

    def get_table_schema(self, table: str, schema: str | None = None) -> str | None:
        sqlalchemy = import_optional_dependency("sqlalchemy")

        try:
            metadata_obj = sqlalchemy.MetaData()
            metadata_obj.reflect(bind=self.engine)
            table = sqlalchemy.Table(table, metadata_obj, schema=schema, autoload=True, autoload_with=self.engine)
            return str([(c.name, c.type) for c in table.columns])
        except sqlalchemy.exc.NoSuchTableError:
            return None
