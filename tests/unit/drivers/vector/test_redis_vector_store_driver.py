import pytest
import redis
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.drivers import RedisVectorStoreDriver


class TestRedisVectorStorageDriver:

    @pytest.fixture(autouse=True)
    def mock_redis(self, mocker):
        # Create a fake hgetall response for our mock Redis client
        fake_hgetall_response = {
            b"vector": b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@',
            b"vec_string": b'[1.0, 2.0, 3.0]',
            b"metadata": b'{"foo": "bar"}'
        }

        # Mock Redis methods that our driver will call
        mocker.patch.object(redis.StrictRedis, "hset", return_value=None)
        mocker.patch.object(redis.StrictRedis, "hgetall", return_value=fake_hgetall_response)
        mocker.patch.object(redis.StrictRedis, "keys", return_value=[b"some_namespace:some_vector_id"])

        # If the ft method is being used, mock it directly, but avoid using autospec on the whole Redis object.
        mocker.patch.object(redis.StrictRedis, "ft", return_value=mocker.MagicMock(
            search=mocker.MagicMock(return_value=mocker.MagicMock(docs=[]))))

    @pytest.fixture
    def driver(self):
        return RedisVectorStoreDriver(
            host="localhost",
            port=6379,
            index="test_index",
            db=0,
            embedding_driver=MockEmbeddingDriver()
        )

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([1.0, 2.0, 3.0], vector_id="some_vector_id") == "some_vector_id"

    def test_load_entry(self, driver):
        entry = driver.load_entry("some_vector_id")
        assert entry.id == "some_vector_id"
        assert entry.vector == [1.0, 2.0, 3.0]
        assert entry.meta == {"foo": "bar"}

    def test_load_entries(self, driver):
        entries = driver.load_entries()
        assert len(entries) == 1
        assert entries[0].vector == [1.0, 2.0, 3.0]
        assert entries[0].meta == {"foo": "bar"}

    def test_query(self, driver):
        # Since the mock search result returns empty docs, this should be an empty list
        assert driver.query([1.0, 2.0, 3.0]) == []
