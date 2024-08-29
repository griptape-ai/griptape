import pytest
import redis

from griptape.drivers.memory.conversation.redis_conversation_memory_driver import RedisConversationMemoryDriver
from griptape.memory.structure.base_conversation_memory import BaseConversationMemory

TEST_DATA = '{"runs": [{"input": {"type": "TextArtifact", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "value": "Hello! How can I assist you today?"}}], "metadata": {"foo": "bar"}}'
TEST_MEMORY = '{"type": "ConversationMemory", "runs": [{"type": "Run", "id": "729ca6be5d79433d9762eb06dfd677e2", "input": {"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}}], "max_runs": 2}'
CONVERSATION_ID = "117151897f344ff684b553d0655d8f39"
INDEX = "griptape_conversation"
HOST = "127.0.0.1"
PORT = 6379
PASSWORD = ""


class TestRedisConversationMemoryDriver:
    @pytest.fixture(autouse=True)
    def _mock_redis(self, mocker):
        mocker.patch.object(redis.StrictRedis, "hset", return_value=None)
        mocker.patch.object(redis.StrictRedis, "keys", return_value=[b"test"])
        mocker.patch.object(redis.StrictRedis, "hget", return_value=TEST_DATA)

        fake_redisearch = mocker.MagicMock()
        fake_redisearch.search = mocker.MagicMock(return_value=mocker.MagicMock(docs=[]))
        fake_redisearch.info = mocker.MagicMock(side_effect=Exception("Index not found"))
        fake_redisearch.create_index = mocker.MagicMock(return_value=None)

        mocker.patch.object(redis.StrictRedis, "ft", return_value=fake_redisearch)

    @pytest.fixture()
    def driver(self):
        return RedisConversationMemoryDriver(host=HOST, port=PORT, db=0, index=INDEX, conversation_id=CONVERSATION_ID)

    def test_store(self, driver):
        memory = BaseConversationMemory.from_json(TEST_MEMORY)
        assert driver.store(memory.runs, memory.meta) is None

    def test_load(self, driver):
        runs, metadata = driver.load()
        assert len(runs) == 1
        assert metadata == {"foo": "bar"}

    def test_load_empty(self, mocker, driver):
        mocker.patch.object(redis.StrictRedis, "hget", return_value=None)
        runs, metadata = driver.load()
        assert len(runs) == 0
        assert metadata == {}
