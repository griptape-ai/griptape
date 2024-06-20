from griptape.drivers import AnthropicPromptDriver
from griptape.common import PromptStack
from griptape.artifacts import TextArtifact, ImageArtifact
from unittest.mock import Mock
import pytest


class TestAnthropicPromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")

        mock_client.return_value = Mock(
            messages=Mock(
                create=Mock(
                    return_value=Mock(
                        usage=Mock(input_tokens=5, output_tokens=10), content=[Mock(type="text", text="model-output")]
                    )
                )
            )
        )

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_stream_client = mocker.patch("anthropic.Anthropic")

        mock_stream_client.return_value = Mock(
            messages=Mock(
                create=Mock(
                    return_value=iter(
                        [
                            Mock(type="message_start", message=Mock(usage=Mock(input_tokens=5))),
                            Mock(type="content_block_delta", delta=Mock(type="text_delta", text="model-output")),
                            Mock(type="message_delta", usage=Mock(output_tokens=10)),
                        ]
                    )
                )
            )
        )

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
        if system_enabled:
            prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(TextArtifact("user-input"))
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        prompt_stack.add_assistant_message("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key")
        expected_messages = [
            {"role": "user", "content": "user-input"},
            {"role": "user", "content": "user-input"},
            {
                "content": [
                    {
                        "source": {"data": "aW1hZ2UtZGF0YQ==", "media_type": "image/png", "type": "base64"},
                        "type": "image",
                    }
                ],
                "role": "user",
            },
            {"role": "assistant", "content": "assistant-input"},
        ]

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=[],
            model=driver.model,
            max_tokens=1000,
            temperature=0.1,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if system_enabled else {},
        )
        assert message.value == "model-output"
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

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
        if system_enabled:
            prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(TextArtifact("user-input"))
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        prompt_stack.add_assistant_message("assistant-input")
        expected_messages = [
            {"role": "user", "content": "user-input"},
            {"role": "user", "content": "user-input"},
            {
                "content": [
                    {
                        "source": {"data": "aW1hZ2UtZGF0YQ==", "media_type": "image/png", "type": "base64"},
                        "type": "image",
                    }
                ],
                "role": "user",
            },
            {"role": "assistant", "content": "assistant-input"},
        ]
        driver = AnthropicPromptDriver(model=model, api_key="api-key", stream=True)

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_stream_client.return_value.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=[],
            model=driver.model,
            max_tokens=1000,
            temperature=0.1,
            stream=True,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if system_enabled else {},
        )
        assert event.usage.input_tokens == 5

        event = next(stream)
        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.output_tokens == 10

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        prompt_stack = "prompt-stack"
        driver = AnthropicPromptDriver(model="claude", api_key="api-key")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'messages'"
