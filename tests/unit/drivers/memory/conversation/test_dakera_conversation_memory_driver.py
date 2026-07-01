import json

import pytest

from griptape.drivers.memory.conversation.dakera import DakeraConversationMemoryDriver
from griptape.memory.structure.base_conversation_memory import BaseConversationMemory

TEST_DATA = '{"runs": [{"input": {"type": "TextArtifact", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "value": "Hello! How can I assist you today?"}}], "metadata": {"foo": "bar"}}'
TEST_MEMORY = '{"type": "ConversationMemory", "runs": [{"type": "Run", "id": "729ca6be5d79433d9762eb06dfd677e2", "input": {"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}}], "max_runs": 2}'
CONVERSATION_ID = "117151897f344ff684b553d0655d8f39"


class TestDakeraConversationMemoryDriver:
    @pytest.fixture()
    def client(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.agent_memories.return_value = [{"id": "mem_1", "content": TEST_DATA}]
        return mock_client

    @pytest.fixture()
    def driver(self, client):
        return DakeraConversationMemoryDriver(
            base_url="http://localhost:3000",
            api_key="dk-test",
            conversation_id=CONVERSATION_ID,
            client=client,
        )

    def test_conversation_id_is_used_as_agent_id(self, driver):
        assert driver.conversation_id == CONVERSATION_ID

    def test_requires_non_empty_conversation_id(self, client):
        with pytest.raises(ValueError, match="requires a non-empty conversation_id"):
            DakeraConversationMemoryDriver(conversation_id="", client=client)

    def test_store(self, driver, client):
        memory = BaseConversationMemory.from_json(TEST_MEMORY)

        assert driver.store(memory.runs, memory.meta) is None

        client.store_memory.assert_called_once()
        _, kwargs = client.store_memory.call_args
        assert kwargs["agent_id"] == CONVERSATION_ID
        stored = json.loads(kwargs["content"])
        assert len(stored["runs"]) == 1

    def test_store_replaces_previous_snapshot(self, driver, client):
        client.agent_memories.return_value = [{"id": "old_1"}, {"id": "old_2"}]
        memory = BaseConversationMemory.from_json(TEST_MEMORY)

        driver.store(memory.runs, memory.meta)

        assert client.forget.call_count == 2
        client.forget.assert_any_call(agent_id=CONVERSATION_ID, memory_id="old_1")
        client.forget.assert_any_call(agent_id=CONVERSATION_ID, memory_id="old_2")
        client.store_memory.assert_called_once()

    def test_load(self, driver):
        runs, metadata = driver.load()

        assert len(runs) == 1
        assert metadata == {"foo": "bar"}

    def test_load_empty(self, driver, client):
        client.agent_memories.return_value = []

        runs, metadata = driver.load()

        assert len(runs) == 0
        assert metadata == {}
