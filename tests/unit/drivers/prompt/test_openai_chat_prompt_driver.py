from griptape.artifacts import ImageArtifact, ListArtifact
from griptape.artifacts import TextArtifact
from griptape.drivers import OpenAiChatPromptDriver
from griptape.common import PromptStack
from griptape.tokenizers import OpenAiTokenizer
from unittest.mock import Mock
from tests.mocks.mock_tokenizer import MockTokenizer
import pytest


class TestOpenAiChatPromptDriverFixtureMixin:
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[Mock(message=Mock(content="model-output"))],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_chat_create

    @pytest.fixture
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_chat_create.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="model-output"))], usage=None),
                Mock(choices=None, usage=Mock(prompt_tokens=5, completion_tokens=10)),
                Mock(choices=[Mock(delta=Mock(content=None))], usage=None),
            ]
        )
        return mock_chat_create

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(
            ListArtifact(
                [TextArtifact("user-input"), ImageArtifact(value=b"image-data", format="png", width=100, height=100)]
            )
        )
        prompt_stack.add_assistant_message("assistant-input")
        return prompt_stack

    @pytest.fixture
    def messages(self):
        return [
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "user-input"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,aW1hZ2UtZGF0YQ=="}},
                ],
            },
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
        event = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model, temperature=driver.temperature, user=driver.user, messages=messages, seed=driver.seed
        )
        assert event.value == "model-output"

    def test_try_run_response_format(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, response_format="json_object"
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            messages=[*messages, {"role": "system", "content": "Provide your response as a valid JSON object."}],
            seed=driver.seed,
            response_format={"type": "json_object"},
        )
        assert message.value == "model-output"
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    def test_try_stream_run(self, mock_chat_completion_stream_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, stream=True)

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            stream=True,
            messages=messages,
            seed=driver.seed,
            stream_options={"include_usage": True},
        )

        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
        event = next(stream)
        assert event.content.text == ""

    def test_try_run_with_max_tokens(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, max_tokens=1)

        # When
        event = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            messages=messages,
            max_tokens=1,
            seed=driver.seed,
        )
        assert event.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        with pytest.raises(Exception) as e:
            driver.try_run("prompt-stack")  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'messages'"

    def test_try_run_throws_when_multiple_choices_returned(self, mock_chat_completion_create, prompt_stack):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, api_key="api-key")
        mock_chat_completion_create.return_value.choices = [Mock(message=Mock(content="model-output"))] * 10

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "Completion with more than one choice is not supported yet."

    def test_custom_tokenizer(self, mock_chat_completion_create, prompt_stack, messages):
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            tokenizer=MockTokenizer(model="mock-model", stop_sequences=["mock-stop"]),
            max_tokens=1,
        )

        # When
        event = driver.try_run(prompt_stack)

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
        assert event.value == "model-output"
