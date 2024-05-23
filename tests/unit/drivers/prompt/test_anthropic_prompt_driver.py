from griptape.drivers import AnthropicPromptDriver
from griptape.common import PromptStack
from unittest.mock import Mock
import pytest


class TestAnthropicPromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")
        mock_content = Mock()
        mock_content.text = "model-output"
        mock_client.return_value.messages.create.return_value.content = [mock_content]
        mock_client.return_value.count_tokens.return_value = 5

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_stream_client = mocker.patch("anthropic.Anthropic")
        mock_chunk = Mock()
        mock_chunk.type = "content_block_delta"
        mock_chunk.delta.text = "model-output"
        mock_stream_client.return_value.messages.create.return_value = iter([mock_chunk])
        mock_stream_client.return_value.count_tokens.return_value = 5

        return mock_stream_client

    @pytest.mark.parametrize("model", [("claude-2.1"), ("claude-2.0")])
    def test_init(self, model):
        assert AnthropicPromptDriver(model=model, api_key="1234")

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_try_run(self, mock_client, model, system_enabled):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        if system_enabled:
            prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key")
        expected_messages = [
            {"role": "user", "content": "generic-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if system_enabled else {},
        )
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_try_stream_run(self, mock_stream_client, model, system_enabled):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        if system_enabled:
            prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        expected_messages = [
            {"role": "user", "content": "generic-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]
        driver = AnthropicPromptDriver(model=model, api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_stream_client.return_value.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            stream=True,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if system_enabled else {},
        )
        assert text_artifact.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        prompt_stack = "prompt-stack"
        driver = AnthropicPromptDriver(model="claude", api_key="api-key")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"
