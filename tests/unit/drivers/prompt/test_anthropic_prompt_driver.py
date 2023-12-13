from griptape.drivers import AnthropicPromptDriver
from griptape.utils import PromptStack
from griptape.tokenizers import AnthropicTokenizer
from unittest.mock import ANY, Mock
import pytest


class TestAnthropicPromptDriver:
    @pytest.fixture
    def mock_completion_create(self, mocker):
        mock_completion_create = mocker.patch("anthropic.Anthropic").return_value.completions.create
        mock_completion_create.return_value.completion = "model-output"
        return mock_completion_create

    @pytest.fixture
    def mock_completion_stream_create(self, mocker):
        mock_completion_create = mocker.patch("anthropic.Anthropic").return_value.completions.create
        mock_chunk = Mock()
        mock_chunk.completion = "model-output"
        mock_completion_create.return_value = iter([mock_chunk])
        return mock_completion_create

    def test_init(self):
        assert AnthropicPromptDriver(model=AnthropicTokenizer.DEFAULT_MODEL, api_key="1234")

    def test_try_run(self, mock_completion_create):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=AnthropicTokenizer.DEFAULT_MODEL, api_key="api-key")

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_completion_create.assert_called_once_with(
            prompt="".join(
                [
                    "\n\n",
                    "Human: generic-input\n\n",
                    "Human: system-input\n\n",
                    "Human: user-input\n\n",
                    "Assistant: assistant-input\n\n",
                    "Assistant:",
                ]
            ),
            stop_sequences=ANY,
            model=driver.model,
            max_tokens_to_sample=ANY,
            temperature=ANY,
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_completion_stream_create):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=AnthropicTokenizer.DEFAULT_MODEL, api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_completion_stream_create.assert_called_once_with(
            prompt="".join(
                [
                    "\n\n",
                    "Human: generic-input\n\n",
                    "Human: system-input\n\n",
                    "Human: user-input\n\n",
                    "Assistant: assistant-input\n\n",
                    "Assistant:",
                ]
            ),
            stop_sequences=ANY,
            model=driver.model,
            max_tokens_to_sample=ANY,
            temperature=ANY,
            stream=driver.stream,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        prompt_stack = "prompt-stack"
        driver = AnthropicPromptDriver(model=AnthropicTokenizer.DEFAULT_MODEL, api_key="api-key")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"
