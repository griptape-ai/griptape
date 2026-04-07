import json
import os

import pytest

from griptape.artifacts import BaseArtifact
from griptape.drivers.memory.conversation.griptape_cloud import GriptapeCloudConversationMemoryDriver
from griptape.memory.structure import Run

TEST_CONVERSATION = '{"type": "SummaryConversationMemory", "runs": [{"type": "Run", "id": "729ca6be5d79433d9762eb06dfd677e2", "input": {"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}, "output": {"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}}], "max_runs": 2}'


class TestGriptapeCloudConversationMemoryDriver:
    @pytest.fixture(autouse=True)
    def _mock_requests(self, mocker):
        def request(*args, **kwargs):
            if args[0] == "get":
                if "/messages" in str(args[1]):
                    thread_id = args[1].split("/")[-2]
                    return mocker.Mock(
                        raise_for_status=lambda: None,
                        json=lambda: {
                            "messages": [
                                {
                                    "message_id": f"{thread_id}_message",
                                    "input": '{"type": "TextArtifact", "id": "1234", "value": "Hi There, Hello"}',
                                    "output": '{"type": "TextArtifact", "id": "123", "value": "Hello! How can I assist you today?"}',
                                    "metadata": {"run_id": "1234"} if thread_id != "no_meta" else {},
                                }
                            ]
                        }
                        if thread_id != "no_messages"
                        else {"messages": []},
                        status_code=200,
                    )
                if "/threads/" in str(args[1]):
                    thread_id = args[1].split("/")[-1]
                    return mocker.Mock(
                        # raise for status if thread_id is == not_found
                        raise_for_status=lambda: None if thread_id != "not_found" else ValueError,
                        json=lambda: {
                            "metadata": {"foo": "bar"},
                            "name": "test",
                            "thread_id": thread_id,
                        },
                        status_code=200 if thread_id != "not_found" else 404,
                    )
                if "/threads?alias=" in str(args[1]):
                    alias = args[1].split("=")[-1]
                    return mocker.Mock(
                        raise_for_status=lambda: None,
                        json=lambda: {"threads": [{"thread_id": alias, "alias": alias, "metadata": {"foo": "bar"}}]}
                        if alias != "not_found"
                        else {"threads": []},
                        status_code=200,
                    )
                return mocker.Mock()
            if args[0] == "post":
                if str(args[1]).endswith("/threads"):
                    body = kwargs["json"]
                    body["thread_id"] = "test"
                    return mocker.Mock(
                        raise_for_status=lambda: None,
                        json=lambda: body,
                    )
                return mocker.Mock(
                    raise_for_status=lambda: None,
                    json=lambda: {"message_id": "test"},
                )
            return mocker.Mock(
                raise_for_status=lambda: None,
            )

        mocker.patch(
            "requests.request",
            side_effect=request,
        )

    @pytest.fixture()
    def driver(self):
        return GriptapeCloudConversationMemoryDriver(api_key="test", thread_id="test")

    def test_no_api_key(self):
        with pytest.raises(ValueError):
            GriptapeCloudConversationMemoryDriver(api_key=None, thread_id="test")

    def test_thread_id(self):
        driver = GriptapeCloudConversationMemoryDriver(api_key="test")
        assert driver.thread_id is None
        assert driver.thread.get("thread_id") == "test"
        assert driver.thread_id == "test"
        os.environ["GT_CLOUD_THREAD_ID"] = "test_env"
        driver = GriptapeCloudConversationMemoryDriver(api_key="test")
        assert driver.thread_id is None
        assert driver.thread.get("thread_id") == "test_env"
        assert driver.thread_id == "test_env"
        os.environ.pop("GT_CLOUD_THREAD_ID")

    def test_thread_alias(self):
        driver = GriptapeCloudConversationMemoryDriver(api_key="test", alias="test")
        assert driver.thread_id is None
        assert driver.thread.get("thread_id") == "test"
        assert driver.thread_id == "test"
        assert driver.alias == "test"

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
        assert metadata == {"foo": "bar"}

    def test_load_no_message_meta(self, driver):
        driver.thread_id = "no_meta"
        runs, metadata = driver.load()
        assert len(runs) == 1
        assert metadata == {"foo": "bar"}
