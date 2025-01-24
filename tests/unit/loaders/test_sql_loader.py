import pytest
from sqlalchemy.pool import StaticPool

from griptape.drivers.sql.sql_driver import SqlDriver
from griptape.loaders import SqlLoader

MAX_TOKENS = 50


class TestSqlLoader:
    @pytest.fixture()
    def loader(self):
        sql_loader = SqlLoader(
            sql_driver=SqlDriver(
                engine_url="sqlite:///:memory:",
                create_engine_params={"connect_args": {"check_same_thread": False}, "poolclass": StaticPool},
            ),
        )

        sql_loader.sql_driver.execute_query(
            "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER, city TEXT);"
        )
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
        artifact = loader.load("SELECT * FROM test_table;")

        assert len(artifact) == 3
        assert artifact[0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
        assert artifact[1].value == "id: 2\nname: Bob\nage: 30\ncity: Los Angeles"
        assert artifact[2].value == "id: 3\nname: Charlie\nage: 22\ncity: Chicago"

    def test_load_collection(self, loader):
        sources = ["SELECT * FROM test_table LIMIT 1;", "SELECT * FROM test_table LIMIT 2;"]
        artifacts = loader.load_collection(sources)

        assert list(artifacts.keys()) == [
            loader.to_key("SELECT * FROM test_table LIMIT 1;"),
            loader.to_key("SELECT * FROM test_table LIMIT 2;"),
        ]

        assert artifacts[loader.to_key(sources[0])][0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
        assert artifacts[loader.to_key(sources[1])][0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
