import json

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
USERNAME = "default"
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
        return RedisConversationMemoryDriver(
            host=HOST, port=PORT, username=USERNAME, db=0, index=INDEX, conversation_id=CONVERSATION_ID
        )

    def test_store(self, driver):
        memory = BaseConversationMemory.from_json(TEST_MEMORY)
        assert driver.store(memory.runs, memory.meta) is None

    @pytest.mark.parametrize("connection_params", [{}, {"host": HOST}, {"port": PORT}, {"host": HOST, "port": PORT}])
    def test_injected_client(self, mocker, connection_params):
        client = mocker.MagicMock(spec=redis.Redis)
        client.hget.return_value = TEST_DATA
        constructor = mocker.patch.object(redis, "Redis")
        driver = RedisConversationMemoryDriver(
            client=client, index=INDEX, conversation_id=CONVERSATION_ID, **connection_params
        )

        assert driver.client is client
        constructor.assert_not_called()
        runs, metadata = driver.load()
        client.hget.assert_called_once_with(INDEX, CONVERSATION_ID)
        assert len(runs) == 1
        assert metadata == {"foo": "bar"}
        driver.store(runs, metadata)
        client.hset.assert_called_once()
        index, conversation_id, stored_json = client.hset.call_args.args
        assert (index, conversation_id) == (INDEX, CONVERSATION_ID)
        stored = json.loads(stored_json)
        assert stored["metadata"] == metadata
        assert stored["runs"][0]["input"]["value"] == "Hi There, Hello"
        assert stored["runs"][0]["output"]["value"] == "Hello! How can I assist you today?"

    def test_create_client(self, mocker):
        constructor = mocker.patch.object(redis, "Redis")
        driver = RedisConversationMemoryDriver(
            host=HOST, port=PORT, username=USERNAME, password=PASSWORD, db=1, index=INDEX
        )

        assert driver.client is constructor.return_value
        constructor.assert_called_once_with(
            host=HOST, port=PORT, username=USERNAME, password=PASSWORD, db=1, decode_responses=False
        )

    @pytest.mark.parametrize("connection_params", [{}, {"host": HOST}, {"port": PORT}])
    def test_missing_connection_parameters(self, mocker, connection_params):
        constructor = mocker.patch.object(redis, "Redis")

        with pytest.raises(ValueError, match="host and port are required when client is not provided"):
            RedisConversationMemoryDriver(index=INDEX, **connection_params)

        constructor.assert_not_called()

    def test_load(self, driver):
        runs, metadata = driver.load()
        assert len(runs) == 1
        assert metadata == {"foo": "bar"}

    def test_load_empty(self, mocker, driver):
        mocker.patch.object(redis.StrictRedis, "hget", return_value=None)
        runs, metadata = driver.load()
        assert len(runs) == 0
        assert metadata == {}
