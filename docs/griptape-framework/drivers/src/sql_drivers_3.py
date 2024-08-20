import os

import snowflake.connector
from snowflake.connector import SnowflakeConnection

from griptape.drivers import SnowflakeSqlDriver


def get_snowflake_connection() -> SnowflakeConnection:
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


driver = SnowflakeSqlDriver(connection_func=get_snowflake_connection)

driver.execute_query("select * from people;")
