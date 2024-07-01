from griptape.common.prompt_stack.contents.text_delta_message_content import TextDeltaMessageContent
from griptape.drivers import OllamaPromptDriver
from griptape.common import PromptStack
from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
import pytest


class TestOllamaPromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("ollama.Client")

        mock_client.return_value.chat.return_value = {"message": {"content": "model-output"}}

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_stream_client = mocker.patch("ollama.Client")
        mock_stream_client.return_value.chat.return_value = iter([{"message": {"content": "model-output"}}])

        return mock_stream_client

    def test_init(self):
        assert OllamaPromptDriver(model="llama")

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
        driver = OllamaPromptDriver(model="llama")
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

    def test_try_run_bad_response(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        driver = OllamaPromptDriver(model="llama")
        mock_client.return_value.chat.return_value = "bad-response"

        # When/Then
        with pytest.raises(Exception, match="invalid model response"):
            driver.try_run(prompt_stack)

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
        driver = OllamaPromptDriver(model="llama", stream=True)

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

    def test_try_stream_bad_response(self, mock_stream_client):
        # Given
        prompt_stack = PromptStack()
        driver = OllamaPromptDriver(model="llama", stream=True)
        mock_stream_client.return_value.chat.return_value = "bad-response"

        # When/Then
        with pytest.raises(Exception, match="invalid model response"):
            next(driver.try_stream(prompt_stack))
