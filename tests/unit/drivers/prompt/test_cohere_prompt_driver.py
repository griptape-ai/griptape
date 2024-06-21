from unittest.mock import Mock

import pytest

from griptape.common import MessageStack
from griptape.drivers import CoherePromptDriver


class TestCoherePromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_client.chat.return_value = Mock(
            text="model-output", meta=Mock(tokens=Mock(input_tokens=5, output_tokens=10))
        )

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_client.chat_stream.return_value = iter(
            [
                Mock(text="model-output", event_type="text-generation"),
                Mock(response=Mock(meta=Mock(tokens=Mock(input_tokens=5, output_tokens=10))), event_type="stream-end"),
            ]
        )

        return mock_client

    @pytest.fixture(autouse=True)
    def mock_tokenizer(self, mocker):
        return mocker.patch("griptape.tokenizers.CohereTokenizer").return_value

    @pytest.fixture
    def message_stack(self):
        message_stack = MessageStack()
        message_stack.add_system_message("system-input")
        message_stack.add_user_message("user-input")
        message_stack.add_assistant_message("assistant-input")
        return message_stack

    def test_init(self):
        assert CoherePromptDriver(model="command", api_key="foobar")

    def test_try_run(self, mock_client, message_stack):  # pyright: ignore
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key")

        # When
        text_artifact = driver.try_run(message_stack)

        # Then
        mock_client.chat.assert_called_once_with(
            chat_history=[{"content": [{"text": "user-input"}], "role": "USER"}],
            max_tokens=None,
            message="assistant-input",
            preamble="system-input",
            stop_sequences=[],
            temperature=0.1,
        )

        assert text_artifact.value == "model-output"
        assert text_artifact.usage.input_tokens == 5
        assert text_artifact.usage.output_tokens == 10

    def test_try_stream_run(self, mock_stream_client, message_stack):  # pyright: ignore
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key", stream=True)

        # When
        stream = driver.try_stream(message_stack)
        event = next(stream)

        # Then

        mock_stream_client.chat_stream.assert_called_once_with(
            chat_history=[{"content": [{"text": "user-input"}], "role": "USER"}],
            max_tokens=None,
            message="assistant-input",
            preamble="system-input",
            stop_sequences=[],
            temperature=0.1,
        )

        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
