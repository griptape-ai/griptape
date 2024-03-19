from google.generativeai.types import GenerationConfig
from griptape.drivers import GooglePromptDriver
from griptape.utils import PromptStack
from unittest.mock import Mock
from tests.mocks.mock_tokenizer import MockTokenizer
import pytest


class TestGooglePromptDriver:
    @pytest.fixture
    def mock_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.start_chat.return_value.send_message.return_value = Mock(text="model-output")

        return mock_generative_model

    @pytest.fixture
    def mock_stream_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.start_chat.return_value.send_message.return_value = iter(
            [Mock(text="model-output")]
        )

        return mock_generative_model

    def test_init(self):
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")
        assert driver

    def test_try_run(self, mock_generative_model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = GooglePromptDriver(
            model="gemini-pro", api_key="api-key", tokenizer=MockTokenizer(model="gemini-pro"), top_p=0.5, top_k=50
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_generative_model.return_value.start_chat.assert_called_once_with(
            history=[
                {"parts": ["generic-input"], "role": "user"},
                {"parts": ["system-input"], "role": "user"},
                {"parts": ["Understood."], "role": "model"},
                {"parts": ["user-input"], "role": "user"},
            ]
        )
        mock_generative_model.return_value.start_chat.return_value.send_message.assert_called_once_with(
            "assistant-input",
            generation_config=GenerationConfig(
                max_output_tokens=995, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=["<|Response|>"]
            ),
        )
        assert text_artifact.value == "model-output"

    def test_try_stream(self, mock_stream_generative_model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = GooglePromptDriver(
            model="gemini-pro",
            api_key="api-key",
            stream=True,
            tokenizer=MockTokenizer(model="gemini-pro"),
            top_p=0.5,
            top_k=50,
        )

        # When
        text_artifact_stream = driver.try_stream(prompt_stack)

        # Then
        text_artifact = next(text_artifact_stream)
        mock_stream_generative_model.return_value.start_chat.assert_called_once_with(
            history=[
                {"parts": ["generic-input"], "role": "user"},
                {"parts": ["system-input"], "role": "user"},
                {"parts": ["Understood."], "role": "model"},
                {"parts": ["user-input"], "role": "user"},
            ]
        )
        mock_stream_generative_model.return_value.start_chat.return_value.send_message.assert_called_once_with(
            "assistant-input",
            stream=True,
            generation_config=GenerationConfig(
                max_output_tokens=995, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=["<|Response|>"]
            ),
        )
        assert text_artifact.value == "model-output"
