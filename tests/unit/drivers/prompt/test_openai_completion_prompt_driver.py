from griptape.drivers import OpenAiCompletionPromptDriver
from griptape.common import PromptStack
from unittest.mock import ANY, Mock
from griptape.tokenizers import OpenAiTokenizer
import pytest


class TestOpenAiCompletionPromptDriverFixtureMixin:
    @pytest.fixture
    def mock_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.completions.create
        mock_choice = Mock()
        mock_choice.text = "model-output"
        mock_chat_create.return_value.choices = [mock_choice]
        return mock_chat_create

    @pytest.fixture
    def mock_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.completions.create
        mock_chunk = Mock()
        mock_choice = Mock()
        mock_choice.text = "model-output"
        mock_chunk.choices = [mock_choice]
        mock_chat_create.return_value = iter([mock_chunk])
        return mock_chat_create

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        return prompt_stack

    @pytest.fixture
    def prompt(self):
        return "".join(
            [
                "generic-input\n\n",
                "system-input\n\n",
                "User: user-input\n\n",
                "Assistant: assistant-input\n\n",
                "Assistant:",
            ]
        )


class TestOpenAiCompletionPromptDriver(TestOpenAiCompletionPromptDriverFixtureMixin):
    def test_init(self):
        assert OpenAiCompletionPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

    def test_try_run(self, mock_completion_create, prompt_stack, prompt):
        # Given
        driver = OpenAiCompletionPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_completion_create.assert_called_once_with(
            model=driver.model,
            max_tokens=ANY,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            prompt=prompt,
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_completion_stream_create, prompt_stack, prompt):
        # Given
        driver = OpenAiCompletionPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_completion_stream_create.assert_called_once_with(
            model=driver.model,
            max_tokens=ANY,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            stream=True,
            prompt=prompt,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        driver = OpenAiCompletionPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        with pytest.raises(Exception) as e:
            driver.try_run("prompt-stack")  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_completion_create, prompt_stack):
        # Given
        driver = OpenAiCompletionPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
        mock_completion_create.return_value.choices = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == "Completion with more than one choice is not supported yet."
