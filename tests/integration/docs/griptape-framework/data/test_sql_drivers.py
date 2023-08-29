import pytest
import re
from sqlalchemy.exc import OperationalError

class TestSqlDrivers:
    def test_sql_driver(self):
        from griptape.drivers import SqlDriver

        driver = SqlDriver(
            engine_url="sqlite:///:memory:"
        )

        with pytest.raises(OperationalError):
            driver.execute_query("select * from people;")


    def test_redshift_driver(self):
        import boto3
        import os
        from griptape.drivers import AmazonRedshiftSqlDriver

        session = boto3.Session(region_name=os.getenv('AWS_DEFAULT_REGION'))

        driver = AmazonRedshiftSqlDriver(
            database=os.getenv("REDSHIFT_DATABASE"),
            session=session,
            cluster_identifier=os.getenv('REDSHIFT_CLUSTER_IDENTIFIER'),
        )

        results = driver.execute_query("select * from people;")

        assert results is not None

    def test_snowflake_sql_driver(self):
        import os
        import snowflake.connector
        from snowflake.connector import SnowflakeConnection
        from griptape.drivers import SnowflakeSqlDriver

        def get_snowflake_connection() -> SnowflakeConnection:
            return snowflake.connector.connect(
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
            )

        driver = SnowflakeSqlDriver(connection_func=get_snowflake_connection)

        results = driver.execute_query("select * from people;")

        assert results is not None
        assert results[0] is not None
        assert results[0].cells is not None
        assert re.search('john', results[0].cells['first_name'], re.IGNORECASE)
