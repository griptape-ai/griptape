class TestSqlClient:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/sql-client/
    """

    def test_sql_client(self):
        from griptape.tools import SqlClient
        from griptape.loaders import SqlLoader
        from griptape.drivers import SqlDriver

        client = SqlClient(
            table_name="users",
            sql_loader=SqlLoader(sql_driver=SqlDriver(engine_url="sqlite:///:memory:")),
        )

        assert client is not None
