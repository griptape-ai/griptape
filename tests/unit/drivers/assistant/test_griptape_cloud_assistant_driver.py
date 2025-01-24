from unittest.mock import ANY, call

import pytest
import requests

from griptape.artifacts import TextArtifact
from griptape.drivers.assistant.griptape_cloud import GriptapeCloudAssistantDriver


class TestGriptapeCloudAssistantDriver:
    @pytest.fixture(autouse=True)
    def mock_requests_post(self, mocker):
        def request(*args, **kwargs):
            if "runs" in args[0]:
                mock_response = mocker.Mock()
                mock_response.json.return_value = {"assistant_run_id": "1"}

                return mock_response
            elif "threads" in args[0]:
                mock_response = mocker.Mock()
                if "alias" in kwargs["json"] and kwargs["json"]["alias"] in (
                    "already_exists",
                    "gone_and_then_exists",
                ):
                    mock_response.raise_for_status.side_effect = requests.HTTPError(
                        response=mocker.Mock(status_code=400)
                    )
                else:
                    mock_response.json.return_value = {"thread_id": "1"}
                return mock_response
            else:
                return mocker.Mock(
                    raise_for_status=lambda: None,
                )

        return mocker.patch(
            "requests.post",
            side_effect=request,
        )

    @pytest.fixture(autouse=True)
    def mock_requests_get(self, mocker):
        def request(*args, **kwargs):
            if "events" in args[0]:
                mock_response = mocker.Mock()
                mock_response.json.return_value = {
                    "events": [
                        {
                            "origin": "ASSISTANT",
                            "type": "FooBarEvent",
                            "payload": {
                                "type": "FooBarEvent",
                            },
                        },
                        {
                            "origin": "ASSISTANT",
                            "type": "FinishStructureRunEvent",
                            "payload": {
                                "type": "FinishStructureRunEvent",
                                "output_task_input": {
                                    "type": "TextArtifact",
                                    "value": "foo bar",
                                },
                                "output_task_output": {
                                    "type": "TextArtifact",
                                    "value": "foo bar",
                                },
                            },
                        },
                        {
                            "origin": "ASSISTANT",
                            "type": "FOO",
                            "payload": {
                                "type": "FinishStructureRunEvent",
                                "output_task_input": {
                                    "type": "TextArtifact",
                                    "value": "foo bar",
                                },
                                "output_task_output": {
                                    "type": "TextArtifact",
                                    "value": "foo bar",
                                },
                            },
                        },
                        {
                            "origin": "FOO",
                        },
                    ],
                    "next_offset": 0,
                }

                return mock_response
            elif "threads" in args[0]:
                mock_response = mocker.Mock()
                if "alias" in kwargs["params"] and kwargs["params"]["alias"] in ("gone_and_then_exists"):
                    mock_response.json.return_value = {"threads": []}
                else:
                    mock_response.json.return_value = {
                        "threads": [
                            {
                                "thread_id": "1",
                                "alias": kwargs["params"]["alias"],
                            }
                        ]
                    }
                return mock_response
            else:
                return mocker.Mock(
                    raise_for_status=lambda: None,
                )

        return mocker.patch(
            "requests.get",
            side_effect=request,
        )

    @pytest.fixture()
    def mock_requests_get_empty(self, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "events": [],
            "next_offset": 0,
        }
        return mocker.patch("requests.get", return_value=mock_response)

    @pytest.fixture()
    def driver(self):
        return GriptapeCloudAssistantDriver(
            base_url="https://cloud-foo.griptape.ai",
            api_key="foo bar",
            assistant_id="1",
        )

    @pytest.mark.parametrize("thread_id", ["1", None])
    @pytest.mark.parametrize("autocreate_thread", [True, False])
    @pytest.mark.parametrize("thread_alias", ["foo", "already_exists", "gone_and_then_exists", None])
    @pytest.mark.parametrize("stream", [True, False])
    def test_run(
        self, driver, mock_requests_get, mock_requests_post, thread_id, autocreate_thread, thread_alias, stream
    ):
        driver.thread_id = thread_id
        driver.auto_create_thread = autocreate_thread
        driver.stream = stream
        driver.thread_alias = thread_alias

        # A thread that is missing on the query call and then exists on the second call
        if thread_id is None and autocreate_thread and thread_alias == "gone_and_then_exists":
            with pytest.raises(requests.HTTPError):
                driver.run(TextArtifact("foo bar"))
        else:
            result = driver.run(TextArtifact("foo bar"))
            assert isinstance(result, TextArtifact)
            assert result.value == "foo bar"
            assert result.meta == {
                "assistant_id": driver.assistant_id,
                "assistant_run_id": "1",
                "thread_id": driver.thread_id,
            }

        # Create or find thread
        if thread_id is None and autocreate_thread:
            if thread_alias is None:
                # Assert that a non-aliased Thread was created
                call_1 = mock_requests_post.call_args_list[0]
                assert "threads" in call_1.args[0]
                if thread_alias is None:
                    assert call_1.kwargs["json"] == {"name": ANY}
                else:
                    assert call_1.kwargs["json"] == {"name": ANY, "alias": driver.thread_alias}
            else:
                # Assert that we tried to find the Thread by alias
                call_1 = mock_requests_get.call_args_list[0]
                assert "threads" in call_1.args[0]
                assert call_1.kwargs["params"] == {"alias": driver.thread_alias}

                # If no thread was found, create a new one
                if thread_alias in ("gone_and_then_exists"):
                    # Assert that we tried to create a new Thread
                    call_2 = mock_requests_post.call_args_list[0]
                    assert "threads" in call_2.args[0]
                    assert call_2.kwargs["json"] == {"alias": driver.thread_alias, "name": ANY}
                else:
                    call_2 = mock_requests_post.call_args_list[0]
                    assert "runs" in call_2.args[0]
                    assert call_2.kwargs["json"] == {
                        "args": ["foo bar"],
                        "stream": stream,
                        "thread_id": driver.thread_id,
                        "input": None,
                        "additional_ruleset_ids": [],
                        "additional_knowledge_base_ids": [],
                        "additional_structure_ids": [],
                        "additional_tool_ids": [],
                    }
        else:
            call_1 = mock_requests_post.call_args_list[0]
            assert "runs" in call_1.args[0]
            assert call_1.kwargs["json"] == {
                "args": ["foo bar"],
                "stream": stream,
                "thread_id": thread_id,
                "input": None,
                "additional_ruleset_ids": [],
                "additional_knowledge_base_ids": [],
                "additional_structure_ids": [],
                "additional_tool_ids": [],
            }

    def test_timeout_run(self, driver, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "events": [],
            "next_offset": 0,
        }
        mock_requests_get_empty = mocker.patch("requests.get", return_value=mock_response)

        driver.max_attempts = 1
        with pytest.raises(TimeoutError):
            driver.run(TextArtifact("foo bar"))

        expected_calls = [
            call(
                "https://cloud-foo.griptape.ai/api/assistant-runs/1/events",
                params={"offset": 0},
                headers={"Authorization": "Bearer foo bar"},
            ),
            call(
                "https://cloud-foo.griptape.ai/api/assistant-runs/1/events",
                params={"offset": 0},
                headers={"Authorization": "Bearer foo bar"},
            ),
        ]
        mock_requests_get_empty.assert_has_calls(expected_calls)
