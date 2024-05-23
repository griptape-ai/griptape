import datetime

from transformers import AutoTokenizer

from griptape.drivers import OpenAiChatPromptDriver
from griptape.tokenizers.huggingface_tokenizer import HuggingFaceTokenizer
from griptape.common import PromptStack
from griptape.tokenizers import OpenAiTokenizer
from unittest.mock import Mock
import pytest


class TestOpenAiChatPromptDriverFixtureMixin:
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.with_raw_response.create
        mock_choice = Mock()
        mock_choice.message.content = "model-output"
        mock_chat_create.return_value.headers = {}
        mock_chat_create.return_value.parse.return_value.choices = [mock_choice]
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

    def test_try_run_max_tokens_limited_by_tokenizer(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        max_tokens_request = 9999999
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, max_tokens=max_tokens_request
        )
        tokens_left = driver.tokenizer.count_input_tokens_left(driver._prompt_stack_to_messages(prompt_stack))

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=messages,
            max_tokens=max_tokens_request,
            seed=driver.seed,
        )
        assert max_tokens_request > tokens_left
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
        mock_chat_completion_create.return_value.parse.return_value.choices = [choices]

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == "Completion with more than one choice is not supported yet."

    def test_token_count(self, prompt_stack, messages):
        # Given
        mock_tokenizer = Mock(spec=OpenAiTokenizer)
        mock_tokenizer.count_tokens.return_value = 42
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, tokenizer=mock_tokenizer)

        # When
        token_count = driver.token_count(prompt_stack)

        # Then
        mock_tokenizer.count_tokens.assert_called_once_with(messages)
        assert token_count == 42

        # Given
        mock_tokenizer = Mock()
        mock_tokenizer.count_tokens.return_value = 42
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, tokenizer=mock_tokenizer)

        # When
        token_count = driver.token_count(prompt_stack)

        # Then
        mock_tokenizer.count_tokens.assert_called_once_with(driver.prompt_stack_to_string(prompt_stack))
        assert token_count == 42

    def test_max_output_tokens(self, messages):
        # Given
        mock_tokenizer = Mock()
        mock_tokenizer.count_output_tokens_left.return_value = 42
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, tokenizer=mock_tokenizer, max_tokens=45
        )

        # When
        max_output_tokens = driver.max_output_tokens(messages)

        # Then
        mock_tokenizer.count_output_tokens_left.assert_called_once_with(messages)
        assert max_output_tokens == 42

    def test_max_output_tokens_with_max_tokens(self, messages):
        max_tokens = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, max_tokens=42
        ).max_output_tokens(messages)

        assert max_tokens == 42

    def test_extract_ratelimit_metadata(self):
        response_with_headers = OpenAiApiResponseWithHeaders()
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
        driver._extract_ratelimit_metadata(response_with_headers)

        assert driver._ratelimit_requests_remaining == response_with_headers.remaining_requests
        assert driver._ratelimit_tokens_remaining == response_with_headers.remaining_tokens
        assert driver._ratelimit_request_limit == response_with_headers.limit_requests
        assert driver._ratelimit_token_limit == response_with_headers.limit_tokens

        # Assert that the reset times are within one second of the expected value.
        expected_request_reset_time = datetime.datetime.now() + datetime.timedelta(
            seconds=response_with_headers.reset_requests_in
        )
        expected_token_reset_time = datetime.datetime.now() + datetime.timedelta(
            seconds=response_with_headers.reset_tokens_in
        )

        assert driver._ratelimit_requests_reset_at is not None
        assert abs(driver._ratelimit_requests_reset_at - expected_request_reset_time) < datetime.timedelta(seconds=1)
        assert driver._ratelimit_tokens_reset_at is not None
        assert abs(driver._ratelimit_tokens_reset_at - expected_token_reset_time) < datetime.timedelta(seconds=1)

    def test_extract_ratelimit_metadata_with_subsecond_reset_times(self):
        response_with_headers = OpenAiApiResponseWithHeaders(
            reset_requests_in=1, reset_requests_in_unit="ms", reset_tokens_in=10, reset_tokens_in_unit="ms"
        )
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, api_key="api-key")
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
        driver._extract_ratelimit_metadata(response_with_headers)

        # Assert that the reset times are within one second of the expected value. With a sub-second reset time,
        # this is rounded up to one second in the future.
        expected_request_reset_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
        expected_token_reset_time = datetime.datetime.now() + datetime.timedelta(seconds=1)

        assert driver._ratelimit_requests_reset_at is not None
        assert abs(driver._ratelimit_requests_reset_at - expected_request_reset_time) < datetime.timedelta(seconds=1)
        assert driver._ratelimit_tokens_reset_at is not None
        assert abs(driver._ratelimit_tokens_reset_at - expected_token_reset_time) < datetime.timedelta(seconds=1)

    def test_extract_ratelimit_metadata_missing_headers(self):
        class OpenAiApiResponseNoHeaders:
            @property
            def headers(self):
                return {}

        response_without_headers = OpenAiApiResponseNoHeaders()

        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
        driver._extract_ratelimit_metadata(response_without_headers)

        assert driver._ratelimit_request_limit is None
        assert driver._ratelimit_requests_remaining is None
        assert driver._ratelimit_requests_reset_at is None
        assert driver._ratelimit_token_limit is None
        assert driver._ratelimit_tokens_remaining is None
        assert driver._ratelimit_tokens_reset_at is None

    def test_custom_tokenizer(self, mock_chat_completion_create, prompt_stack, messages):
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            tokenizer=HuggingFaceTokenizer(tokenizer=AutoTokenizer.from_pretrained("gpt2"), max_output_tokens=1000),
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
            messages=messages,
            seed=driver.seed,
            max_tokens=1,
        )
        assert text_artifact.value == "model-output"
