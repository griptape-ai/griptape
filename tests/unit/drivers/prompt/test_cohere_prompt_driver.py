from griptape.drivers import CoherePromptDriver
from griptape.utils import PromptStack
from unittest.mock import Mock
import pytest


class TestCoherePromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_client.chat.return_value = Mock(text="model-output")

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_chunk = Mock(text="model-output", event_type="text-generation")
        mock_client.chat_stream.return_value = iter([mock_chunk])

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

        # Then
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_stream_client, prompt_stack):  # pyright: ignore
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        assert text_artifact.value == "model-output"
