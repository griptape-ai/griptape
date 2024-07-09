from griptape.drivers import OpenAiChatPromptDriver
from griptape.tokenizers.huggingface_tokenizer import HuggingFaceTokenizer
from griptape.utils import PromptStack
from griptape.tokenizers import OpenAiTokenizer
from unittest.mock import Mock
import pytest


class TestOpenAiChatPromptDriverFixtureMixin:
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_choice = Mock()
        mock_choice.message.content = "model-output"
        mock_chat_create.return_value.headers = {}
        mock_chat_create.return_value.choices = [mock_choice]
        return mock_chat_create

    @pytest.fixture
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_chunk = Mock()
        mock_choice = Mock()
        mock_choice.delta.content = "model-output"
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
    def messages(self):
        return [
            {"role": "user", "content": "generic-input"},
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]


class OpenAiApiResponseWithHeaders:
    def __init__(
        self,
        reset_requests_in=5,
        reset_requests_in_unit="s",
        reset_tokens_in=10,
        reset_tokens_in_unit="s",
        remaining_requests=123,
        remaining_tokens=234,
        limit_requests=345,
        limit_tokens=456,
    ):
        self.reset_requests_in = reset_requests_in
        self.reset_requests_in_unit = reset_requests_in_unit
        self.reset_tokens_in = reset_tokens_in
        self.reset_tokens_in_unit = reset_tokens_in_unit
        self.remaining_requests = remaining_requests
        self.remaining_tokens = remaining_tokens
        self.limit_requests = limit_requests
        self.limit_tokens = limit_tokens

    @property
    def headers(self):
        return {
            "x-ratelimit-reset-requests": f"{self.reset_requests_in}{self.reset_requests_in_unit}",
            "x-ratelimit-reset-tokens": f"{self.reset_tokens_in}{self.reset_tokens_in_unit}",
            "x-ratelimit-limit-requests": self.limit_requests,
            "x-ratelimit-remaining-requests": self.remaining_requests,
            "x-ratelimit-limit-tokens": self.limit_tokens,
            "x-ratelimit-remaining-tokens": self.remaining_tokens,
        }


class TestOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)

    def test_try_run(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=messages,
            seed=driver.seed,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_response_format(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, response_format="json_object"
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=[*messages, {"role": "system", "content": "Provide your response as a valid JSON object."}],
            seed=driver.seed,
            response_format={"type": "json_object"},
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_chat_completion_stream_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            stream=True,
            messages=messages,
            seed=driver.seed,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_with_max_tokens(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, max_tokens=1)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=messages,
            max_tokens=1,
            seed=driver.seed,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        with pytest.raises(Exception) as e:
            driver.try_run("prompt-stack")  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_chat_completion_create, prompt_stack):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, api_key="api-key")
        mock_chat_completion_create.return_value.choices = [choices]

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == "Completion with more than one choice is not supported yet."

    def test_custom_tokenizer(self, mock_chat_completion_create, prompt_stack, messages):
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            tokenizer=HuggingFaceTokenizer(model="gpt2", max_output_tokens=1000),
            max_tokens=1,
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=[
                {"role": "user", "content": "generic-input"},
                {"role": "system", "content": "system-input"},
                {"role": "user", "content": "user-input"},
                {"role": "assistant", "content": "assistant-input"},
            ],
            seed=driver.seed,
            max_tokens=1,
        )
        assert text_artifact.value == "model-output"
