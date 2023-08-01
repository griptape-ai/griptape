import json
import pytest
from griptape.drivers import RedisVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class MockFTResult:
    def __init__(self, docs):
        self.docs = docs

    def search(self, *args, **kwargs):
        return self


class TestRedisVectorStoreDriver:

    @pytest.fixture(autouse=True)
    def mock_redis(self, mocker):
        mocker.patch("redis.StrictRedis.set", return_value=None)
        mocker.patch("redis.StrictRedis.get",
                     return_value=json.dumps({"vector": [0, 1, 2], "metadata": {"foo": "bar"}}))
        mocker.patch("redis.StrictRedis.keys", return_value=[b'test:foo'])
        # Mocking the query response for testing the query method
        mocker.patch("redis.StrictRedis.ft", return_value=MockFTResult([{'id': 'foo', 'score': 0.9}]))

    @pytest.fixture
    def driver(self):
        return RedisVectorStoreDriver(
            host="localhost",
            port=6379,
            db=0,
            embedding_driver=MockEmbeddingDriver()
        )

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0, 1, 2], vector_id="foo") == "foo"
        assert isinstance(driver.upsert_vector([0, 1, 2]), str)

    def test_load_entry(self, driver):
        entry = driver.load_entry("foo")
        assert entry.id == "foo"
        assert entry.vector == [0, 1, 2]
        assert entry.meta == {"foo": "bar"}

    def test_load_entries(self, driver):
        entries = driver.load_entries()
        assert len(entries) == 1
        assert entries[0].id == "foo"
        assert entries[0].vector == [0, 1, 2]
        assert entries[0].meta == {"foo": "bar"}

    def test_query(self, driver):
        query_result = driver.query("test query", count=1)

        # Verifying the expected properties of the query result
        assert len(query_result) == 1
        assert query_result[0].vector == 'foo'
        assert query_result[0].score == 0.9
        assert query_result[0].meta is None
        assert query_result[0].namespace is None
