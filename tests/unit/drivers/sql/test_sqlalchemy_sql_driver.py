import pytest

from griptape.drivers import SqlalchemySqlDriver


class TestSqlalchemySqlDriver:
    @pytest.fixture
    def driver(self):
        new_driver = SqlalchemySqlDriver(
            engine_url="sqlite:///:memory:"
        )

        new_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);"
        )

        new_driver.execute_query(
            "INSERT INTO test_table (name, age, city) VALUES ('Alice', 25, 'New York');"
        )

        return new_driver

    def test_execute_query(self, driver):
        assert driver.execute_query("SELECT count(*) FROM test_table")[0].cells == [1]
