import pytest

from griptape.drivers import SqlDriver


class TestSqlDriver:
    @pytest.fixture()
    def driver(self):
        new_driver = SqlDriver(engine_url="sqlite:///:memory:")

        new_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);"
        )

        new_driver.execute_query("INSERT INTO test_table (name, age, city) VALUES ('Alice', 25, 'New York');")

        return new_driver

    def test_execute_query(self, driver):
        assert driver.execute_query("SELECT count(*) FROM test_table")[0].cells == {"count(*)": 1}

    def test_execute_query_raw(self, driver):
        assert driver.execute_query_raw("SELECT * FROM test_table") == [
            {"age": 25, "city": "New York", "id": 1, "name": "Alice"}
        ]

    def test_get_table_schema(self, driver):
        assert (
            driver.get_table_schema("test_table")
            == "[('id', INTEGER()), ('name', TEXT()), ('age', INTEGER()), ('city', TEXT())]"
        )

        assert driver.get_table_schema("doesnt-exist") is None
