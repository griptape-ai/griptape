import json
import os

import pytest

from griptape.artifacts import BaseArtifact
from griptape.drivers import GriptapeCloudConversationMemoryDriver
from griptape.memory.structure import Run

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
                                "metadata": {"run_id": "1234"},
                            }
                        ]
                    },
                )
            else:
                thread_id = args[0].split("/")[-1]
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {
                        "metadata": {"foo": "bar"},
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

        def post(*args, **kwargs):
            if str(args[0]).endswith("/threads"):
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {"thread_id": "test", "name": "test"},
                )
            else:
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {"message_id": "test"},
                )

        mocker.patch(
            "requests.post",
            side_effect=post,
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

    def test_thread_id(self):
        driver = GriptapeCloudConversationMemoryDriver(api_key="test")
        assert driver.thread_id == "test"
        os.environ["GT_CLOUD_THREAD_ID"] = "test_env"
        driver = GriptapeCloudConversationMemoryDriver(api_key="test")
        assert driver.thread_id == "test_env"
        driver = GriptapeCloudConversationMemoryDriver(api_key="test", thread_id="test_init")
        assert driver.thread_id == "test_init"

    def test_store(self, driver: GriptapeCloudConversationMemoryDriver):
        runs = [
            Run(input=BaseArtifact.from_dict(run["input"]), output=BaseArtifact.from_dict(run["output"]))
            for run in json.loads(TEST_CONVERSATION)["runs"]
        ]
        assert driver.store(runs, {}) is None

    def test_load(self, driver):
        runs, metadata = driver.load()
        assert len(runs) == 1
        assert runs[0].id == "1234"
        assert metadata == {}
        driver.thread_id = "test_metadata"
        runs, metadata = driver.load()
        assert len(runs) == 1
        assert metadata == {"foo": "bar"}
