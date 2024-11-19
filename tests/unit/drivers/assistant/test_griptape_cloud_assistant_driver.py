from unittest.mock import call

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import GriptapeCloudAssistantDriver


class TestGriptapeCloudAssistantDriver:
    @pytest.fixture(autouse=True)
    def mock_requests_post(self, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"assistant_run_id": 1}

        return mocker.patch("requests.post", return_value=mock_response)

    @pytest.fixture()
    def mock_requests_get(self, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "events": [
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
        return mocker.patch("requests.get", return_value=mock_response)

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

    def test_run(self, driver, mock_requests_post, mock_requests_get):
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, TextArtifact)
        assert result.value == "foo bar"
        mock_requests_post.assert_called_once_with(
            "https://cloud-foo.griptape.ai/api/assistants/1/runs",
            json={
                "args": ["foo bar"],
                "stream": False,
                "thread_id": None,
                "input": None,
                "ruleset_ids": [],
                "additional_ruleset_ids": [],
                "knowledge_base_ids": [],
                "additional_knowledge_base_ids": [],
            },
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_stream_run(self, driver, mock_requests_post, mock_requests_get):
        driver.stream = True
        result = driver.run(TextArtifact("foo bar"))
        assert isinstance(result, TextArtifact)
        assert result.value == "foo bar"
        mock_requests_post.assert_called_once_with(
            "https://cloud-foo.griptape.ai/api/assistants/1/runs",
            json={
                "args": ["foo bar"],
                "stream": True,
                "thread_id": None,
                "input": None,
                "ruleset_ids": [],
                "additional_ruleset_ids": [],
                "knowledge_base_ids": [],
                "additional_knowledge_base_ids": [],
            },
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_timeout_run(self, driver, mock_requests_get_empty):
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
