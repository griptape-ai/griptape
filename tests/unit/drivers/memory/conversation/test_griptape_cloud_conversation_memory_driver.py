import json

import pytest

from griptape.artifacts import BaseArtifact
from griptape.drivers import GriptapeCloudConversationMemoryDriver
from griptape.memory.structure import BaseConversationMemory, ConversationMemory, Run, SummaryConversationMemory

TEST_CONVERSATION = '{"type": "SummaryConversationMemory", "runs": [{"type": "Run", "id": "729ca6be5d79433d9762eb06dfd677e2", "input": {"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}}], "max_runs": 2}'


class TestGriptapeCloudConversationMemoryDriver:
    @pytest.fixture(autouse=True)
    def _mock_requests(self, mocker):
        def get(*args, **kwargs):
            if str(args[0]).endswith("/messages"):
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {
                        "messages": [
                            {
                                "message_id": "123",
                                "input": '{"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}',
                                "output": '{"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}',
                                "index": 0,
                            }
                        ]
                    },
                )
            else:
                thread_id = args[0].split("/")[-1]
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {
                        "metadata": json.loads(TEST_CONVERSATION),
                        "name": "test",
                        "thread_id": "test_metadata",
                    }
                    if thread_id == "test_metadata"
                    else {"name": "test", "thread_id": "test"},
                )

        mocker.patch(
            "requests.get",
            side_effect=get,
        )
        mocker.patch(
            "requests.post",
            return_value=mocker.Mock(
                raise_for_status=lambda: None,
                json=lambda: {"thread_id": "test", "name": "test"},
            ),
        )
        mocker.patch(
            "requests.patch",
            return_value=mocker.Mock(
                raise_for_status=lambda: None,
            ),
        )

    @pytest.fixture()
    def driver(self):
        return GriptapeCloudConversationMemoryDriver(api_key="test", thread_id="test")

    def test_no_api_key(self):
        with pytest.raises(ValueError):
            GriptapeCloudConversationMemoryDriver(api_key=None, thread_id="test")

    def test_no_thread_id(self):
        driver = GriptapeCloudConversationMemoryDriver(api_key="test")
        assert driver.thread_id == "test"

    def test_store(self, driver):
        memory = ConversationMemory(
            runs=[
                Run(input=BaseArtifact.from_dict(run["input"]), output=BaseArtifact.from_dict(run["output"]))
                for run in json.loads(TEST_CONVERSATION)["runs"]
            ],
        )
        assert driver.store(memory) is None

    def test_load(self, driver):
        memory = driver.load()
        assert isinstance(memory, BaseConversationMemory)
        assert len(memory.runs) == 1

    def test_load_metadata(self, driver):
        driver.thread_id = "test_metadata"
        memory = driver.load()
        assert isinstance(memory, SummaryConversationMemory)
        assert len(memory.runs) == 1
