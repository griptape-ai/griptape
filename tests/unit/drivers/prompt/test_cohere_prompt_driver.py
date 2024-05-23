from griptape.drivers import CoherePromptDriver
from griptape.common import PromptStack
from unittest.mock import Mock
import pytest


class TestCoherePromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_client.generate.return_value.generations = [Mock()]
        mock_client.generate.return_value.generations[0].text = "model-output"
        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_chunk = Mock()
        mock_chunk.text = "model-output"
        mock_client.generate.return_value = iter([mock_chunk])
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

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_client, prompt_stack):
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key")
        mock_client.generate.return_value.generations = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "Completion with more than one choice is not supported yet."
