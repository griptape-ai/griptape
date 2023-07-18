import pytest
from sqlalchemy.pool import StaticPool
from griptape import utils
from griptape.drivers import SqlDriver
from griptape.loaders import SqlLoader

MAX_TOKENS = 50


class TestSqlLoader:
    @pytest.fixture
    def loader(self):
        sql_loader = SqlLoader(
            sql_driver=SqlDriver(
                engine_url="sqlite:///:memory:",
                create_engine_params={
                    "connect_args": {
                        "check_same_thread": False
                    },
                    "poolclass": StaticPool
                }
            )
        )

        sql_loader.sql_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);")
        sql_loader.sql_driver.execute_query(
            "INSERT INTO test_table (name, age, city) VALUES ('Alice', 25, 'New York');"
        )
        sql_loader.sql_driver.execute_query(
            "INSERT INTO test_table (name, age, city) VALUES ('Bob', 30, 'Los Angeles');"
        )
        sql_loader.sql_driver.execute_query(
            "INSERT INTO test_table (name, age, city) VALUES ('Charlie', 22, 'Chicago');"
        )

        return sql_loader

    def test_load(self, loader):
        result = loader.load("SELECT * FROM test_table;")

        assert len(result) == 3
        assert result[0].value == {"id": 1, "name": "Alice", "age": 25, "city": "New York"}
        assert result[1].value == {"id": 2, "name": "Bob", "age": 30, "city": "Los Angeles"}
        assert result[2].value == {"id": 3, "name": "Charlie", "age": 22, "city": "Chicago"}

    def test_load_collection(self, loader):
        artifacts = loader.load_collection([
            "SELECT * FROM test_table LIMIT 1;",
            "SELECT * FROM test_table LIMIT 2;"
        ])

        assert list(artifacts.keys()) == [
            utils.str_to_hash("SELECT * FROM test_table LIMIT 1;"),
            utils.str_to_hash("SELECT * FROM test_table LIMIT 2;")
        ]

        assert [a.value for artifact_list in artifacts.values() for a in artifact_list] == [
            {"age": 25, "city": "New York", "id": 1, "name": "Alice"},
            {"age": 25, "city": "New York", "id": 1, "name": "Alice"},
            {"age": 30, "city": "Los Angeles", "id": 2, "name": "Bob"}
        ]
