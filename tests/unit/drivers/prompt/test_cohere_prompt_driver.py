from unittest.mock import Mock

import pytest

from griptape.common import MessageStack
from griptape.drivers import CoherePromptDriver


class TestCoherePromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client")
        mock_client.return_value.chat.return_value = Mock(text="model-output")

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("cohere.Client")
        mock_chunk = Mock(text="model-output", event_type="text-generation")
        mock_client.return_value.chat_stream.return_value = iter([mock_chunk])

        return mock_client

    @pytest.fixture(autouse=True)
    def mock_tokenizer(self, mocker):
        return mocker.patch("griptape.tokenizers.CohereTokenizer").return_value

    @pytest.fixture(params=[True, False])
    def message_stack(self, request):
        message_stack = MessageStack()
        if request.param:
            message_stack.add_system_message("system-input")
        message_stack.add_user_message("user-input")
        message_stack.add_assistant_message("assistant-input")
        message_stack.add_user_message("user-input")
        message_stack.add_assistant_message("assistant-input")
        return message_stack

    def test_init(self):
        assert CoherePromptDriver(model="command", api_key="foobar")

    def test_try_run(self, mock_client, message_stack):
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key")

        # When
        text_artifact = driver.try_run(prompt_stack)
        print(f"Called methods: {mock_client}")

        # Then
        expected_message = "assistant-input"
        expected_history = [
            {"role": "ASSISTANT", "text": "generic-input"},
            {"role": "SYSTEM", "text": "system-input"},
            {"role": "USER", "text": "user-input"},
        ]
        mock_client.return_value.chat.assert_called_once_with(
            message=expected_message,
            temperature=driver.temperature,
            stop_sequences=driver.tokenizer.stop_sequences,
            max_tokens=driver.max_tokens,
            chat_history=expected_history,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_no_history(self, mock_client, prompt_stack):
        # Given
        prompt_stack_no_history = PromptStack()
        prompt_stack_no_history.add_user_input("user-input")
        driver = CoherePromptDriver(model="command", api_key="api-key")

        # When
        text_artifact = driver.try_run(prompt_stack_no_history)

        # Then
        expected_message = "user-input"
        mock_client.return_value.chat.assert_called_once_with(
            message=expected_message,
            temperature=driver.temperature,
            stop_sequences=driver.tokenizer.stop_sequences,
            max_tokens=driver.max_tokens,
        )
        assert text_artifact.value == "model-output"

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
            chat_history=[
                {"content": [{"text": "user-input"}], "role": "USER"},
                {"content": [{"text": "assistant-input"}], "role": "CHATBOT"},
                {"content": [{"text": "user-input"}], "role": "USER"},
            ],
            max_tokens=None,
            message="assistant-input",
            **({"preamble": "system-input"} if message_stack.system_messages else {}),
            stop_sequences=[],
            temperature=0.1,
        )

        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
