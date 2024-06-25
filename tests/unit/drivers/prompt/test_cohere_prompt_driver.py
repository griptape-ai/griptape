from griptape.drivers import CoherePromptDriver
from griptape.utils import PromptStack
from unittest.mock import Mock
import pytest


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

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        return prompt_stack

    def test_init(self):
        assert CoherePromptDriver(model="command", api_key="foobar")

    def test_try_run(self, mock_client, prompt_stack):  # pyright: ignore
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

    def test_try_stream_run(self, mock_stream_client, prompt_stack):  # pyright: ignore
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        assert text_artifact.value == "model-output"
