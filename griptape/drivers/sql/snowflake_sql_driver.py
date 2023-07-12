from typing import Callable, Optional
from griptape.drivers import BaseSqlDriver
from attr import Factory, define, field
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoSuchTableError
from snowflake.connector import SnowflakeConnection


@define
class SnowflakeSqlDriver(BaseSqlDriver):
    snowflake_connection_function: Callable[[], SnowflakeConnection] = field(
        kw_only=True
    )
    engine: Engine = field(
        default=Factory(
            # Creator bypasses the URL param
            # https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine.params.creator
            lambda self: create_engine(
                "snowflake://not@used/db", creator=self.snowflake_connection_function
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    @snowflake_connection_function.validator
    def validate_snowflake_connection_function(
        self, _, snowflake_connection_function: Callable[[], SnowflakeConnection]
    ) -> None:
        snowflake_connection = snowflake_connection_function()
        if not isinstance(snowflake_connection, SnowflakeConnection):
            raise ValueError(
                "The snowflake_connection_function must return a SnowflakeConnection"
            )
        if not snowflake_connection.schema or not snowflake_connection.database:
            raise ValueError(
                "Provide a schema and database for the Snowflake connection"
            )

    @engine.validator
    def validate_engine_url(self, _, engine: Engine) -> None:
        if not engine.url.render_as_string().startswith("snowflake://"):
            raise ValueError("Provide a Snowflake connection")

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
