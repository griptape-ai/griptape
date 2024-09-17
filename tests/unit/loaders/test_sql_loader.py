import pytest
from sqlalchemy.pool import StaticPool

from griptape.drivers import SqlDriver
from griptape.loaders import SqlLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestSqlLoader:
    @pytest.fixture()
    def loader(self):
        sql_loader = SqlLoader(
            sql_driver=SqlDriver(
                engine_url="sqlite:///:memory:",
                create_engine_params={"connect_args": {"check_same_thread": False}, "poolclass": StaticPool},
            ),
            embedding_driver=MockEmbeddingDriver(),
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
        artifacts = loader.load("SELECT * FROM test_table;")

        assert len(artifacts) == 3
        assert artifacts[0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
        assert artifacts[1].value == "id: 2\nname: Bob\nage: 30\ncity: Los Angeles"
        assert artifacts[2].value == "id: 3\nname: Charlie\nage: 22\ncity: Chicago"

        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader):
        sources = ["SELECT * FROM test_table LIMIT 1;", "SELECT * FROM test_table LIMIT 2;"]
        artifacts = loader.load_collection(sources)

        assert list(artifacts.keys()) == [
            loader.to_key("SELECT * FROM test_table LIMIT 1;"),
            loader.to_key("SELECT * FROM test_table LIMIT 2;"),
        ]

        assert artifacts[loader.to_key(sources[0])][0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
        assert artifacts[loader.to_key(sources[1])][0].value == "id: 1\nname: Alice\nage: 25\ncity: New York"
        assert list(artifacts.values())[0][0].embedding == [0, 1]
