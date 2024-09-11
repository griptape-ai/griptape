import sqlite3

import pytest

from griptape.drivers import SqlDriver
from griptape.loaders import SqlLoader
from griptape.tools import SqlTool


class TestSqlTool:
    @pytest.fixture()
    def driver(self):
        new_driver = SqlDriver(engine_url="sqlite:///:memory:")

        new_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);"
        )

        new_driver.execute_query("INSERT INTO test_table (name, age, city) VALUES ('Alice', 25, 'New York');")

        return new_driver

    def test_execute_query(self, driver):
        with sqlite3.connect(":memory:"):
            client = SqlTool(sql_loader=SqlLoader(sql_driver=driver), table_name="test_table", engine_name="sqlite")
            result = client.execute_query({"values": {"sql_query": "SELECT * from test_table;"}})

            assert len(result.value) == 1
            assert result.value[0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"

    def test_execute_query_description(self, driver):
        client = SqlTool(
            sql_loader=SqlLoader(sql_driver=driver),
            table_name="test_table",
            table_description="foobar",
            engine_name="sqlite",
        )
        description = client.activity_description(client.execute_query)

        assert "Can be used to execute sqlite SQL SELECT queries in table test_table" in description
        assert (
            "test_table schema: [('id', INTEGER()), ('name', TEXT()), ('age', INTEGER()), ('city', TEXT())]"
            in description
        )
        assert "test_table description: foobar" in description
