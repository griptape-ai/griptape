from google.generativeai.types import GenerationConfig
from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.drivers import GooglePromptDriver
from griptape.common import MessageStack
from unittest.mock import Mock
import pytest


class TestGooglePromptDriver:
    @pytest.fixture
    def mock_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.generate_content.return_value = Mock(
            text="model-output", usage_metadata=Mock(prompt_token_count=5, candidates_token_count=10)
        )

        return mock_generative_model

    @pytest.fixture
    def mock_stream_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.generate_content.return_value = iter(
            [
                Mock(text="model-output", usage_metadata=Mock(prompt_token_count=5, candidates_token_count=5)),
                Mock(text="model-output", usage_metadata=Mock(prompt_token_count=5, candidates_token_count=5)),
            ]
        )

        return mock_generative_model

    def test_init(self):
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")
        assert driver

    def test_try_run(self, mock_generative_model):
        # Given
        message_stack = MessageStack()
        message_stack.add_system_message("system-input")
        message_stack.add_user_message("user-input")
        message_stack.add_user_message(TextArtifact("user-input"))
        message_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        message_stack.add_assistant_message("assistant-input")
        driver = GooglePromptDriver(model="gemini-pro", api_key="api-key", top_p=0.5, top_k=50)

        # When
        text_artifact = driver.try_run(message_stack)

        # Then
        mock_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["user-input"], "role": "user"},
                {"parts": [{"data": b"image-data", "mime_type": "image/png"}], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
            ],
            generation_config=GenerationConfig(
                max_output_tokens=None, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[]
            ),
        )
        assert text_artifact.value == "model-output"
        assert text_artifact.usage.input_tokens == 5
        assert text_artifact.usage.output_tokens == 10

    def test_try_stream(self, mock_stream_generative_model):
        # Given
        message_stack = MessageStack()
        message_stack.add_system_message("system-input")
        message_stack.add_user_message("user-input")
        message_stack.add_user_message(TextArtifact("user-input"))
        message_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        message_stack.add_assistant_message("assistant-input")
        driver = GooglePromptDriver(model="gemini-pro", api_key="api-key", stream=True, top_p=0.5, top_k=50)

        # When
        stream = driver.try_stream(message_stack)

        # Then
        event = next(stream)
        mock_stream_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["user-input"], "role": "user"},
                {"parts": [{"data": b"image-data", "mime_type": "image/png"}], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
            ],
            stream=True,
            generation_config=GenerationConfig(temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[]),
        )
        assert event.content.text == "model-output"
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 5

        event = next(stream)
        assert event.usage.output_tokens == 5
