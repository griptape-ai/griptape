from griptape.common.prompt_stack.contents.text_delta_message_content import TextDeltaMessageContent
from griptape.drivers import LmStudioPromptDriver
from griptape.common import PromptStack
from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from unittest.mock import Mock
import pytest


class TestLmStudioPromptDriver:
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_function = Mock(arguments='{"foo": "bar"}', id="mock-id")
        mock_function.name = "MockTool_test"
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[Mock(message=Mock(content="model-output"))],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_chat_create

    @pytest.fixture
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_tool_call_delta_header = Mock()
        mock_tool_call_delta_header.name = "MockTool_test"
        mock_tool_call_delta_body = Mock(arguments='{"foo": "bar"}')
        mock_tool_call_delta_body.name = None

        mock_chat_create.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="model-output", tool_calls=None))], usage=None),
                Mock(choices=None, usage=Mock(prompt_tokens=5, completion_tokens=10)),
            ]
        )
        return mock_chat_create

    def test_init(self):
        assert LmStudioPromptDriver(model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")

    def test_try_run(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(
            ListArtifact(
                [TextArtifact("user-input"), ImageArtifact(value=b"image-data", format="png", width=100, height=100)]
            )
        )
        prompt_stack.add_assistant_message("assistant-input")
        driver = LmStudioPromptDriver(model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")
        expected_messages = [
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {"role": "user", "content": "user-input", "images": ["aW1hZ2UtZGF0YQ=="]},
            {"role": "assistant", "content": "assistant-input"},
        ]

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.chat.assert_called_once_with(
            messages=expected_messages,
            model=driver.model,
            options={"temperature": driver.temperature, "stop": [], "num_predict": driver.max_tokens},
        )
        assert message.value == "model-output"
        assert message.usage.input_tokens is None
        assert message.usage.output_tokens is None

    def test_try_stream_run(self, mock_stream_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(
            ListArtifact(
                [TextArtifact("user-input"), ImageArtifact(value=b"image-data", format="png", width=100, height=100)]
            )
        )
        prompt_stack.add_assistant_message("assistant-input")
        expected_messages = [
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {"role": "user", "content": "user-input", "images": ["aW1hZ2UtZGF0YQ=="]},
            {"role": "assistant", "content": "assistant-input"},
        ]
        driver = LmStudioPromptDriver(model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_stream_client.return_value.chat.assert_called_once_with(
            messages=expected_messages,
            model=driver.model,
            options={"temperature": driver.temperature, "stop": [], "num_predict": driver.max_tokens},
            stream=True,
        )
        if isinstance(text_artifact, TextDeltaMessageContent):
            assert text_artifact.text == "model-output"
