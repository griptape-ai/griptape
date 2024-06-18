from google.generativeai.types import GenerationConfig
from griptape.common.prompt_stack.contents.delta_text_prompt_stack_content import DeltaTextPromptStackContent
from griptape.drivers import GooglePromptDriver
from griptape.common import PromptStack
from unittest.mock import Mock
import pytest


class TestGooglePromptDriver:
    @pytest.fixture
    def mock_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.generate_content.return_value = Mock(text="model-output")

        return mock_generative_model

    @pytest.fixture
    def mock_stream_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.generate_content.return_value = iter([Mock(text="model-output")])

        return mock_generative_model

    def test_init(self):
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")
        assert driver

    def test_try_run(self, mock_generative_model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_assistant_message("assistant-input")
        driver = GooglePromptDriver(model="gemini-pro", api_key="api-key", top_p=0.5, top_k=50)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
            ],
            generation_config=GenerationConfig(
                max_output_tokens=None, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[]
            ),
        )
        assert text_artifact.value == "model-output"

    def test_try_stream(self, mock_stream_generative_model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_assistant_message("assistant-input")
        driver = GooglePromptDriver(model="gemini-pro", api_key="api-key", stream=True, top_p=0.5, top_k=50)

        # When
        text_artifact_stream = driver.try_stream(prompt_stack)

        # Then
        text_artifact = next(text_artifact_stream)
        mock_stream_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
            ],
            stream=True,
            generation_config=GenerationConfig(temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[]),
        )
        if isinstance(text_artifact, DeltaTextPromptStackContent):
            assert text_artifact.text == "model-output"
