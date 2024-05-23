from google.generativeai.types import GenerationConfig
from griptape.drivers import GooglePromptDriver
from griptape.common import PromptStack
from unittest.mock import Mock
from tests.mocks.mock_tokenizer import MockTokenizer
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
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        prompt_stack.add_generic_input("generic-input")
        driver = GooglePromptDriver(
            model="gemini-pro", api_key="api-key", tokenizer=MockTokenizer(model="gemini-pro"), top_p=0.5, top_k=50
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
                {"parts": ["generic-input"], "role": "user"},
            ],
            generation_config=GenerationConfig(
                max_output_tokens=997, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=["<|Response|>"]
            ),
        )
        assert text_artifact.value == "model-output"

    def test_try_stream(self, mock_stream_generative_model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        prompt_stack.add_generic_input("generic-input")
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
        mock_stream_generative_model.return_value.generate_content.assert_called_once_with(
            [
                {"parts": ["system-input", "user-input"], "role": "user"},
                {"parts": ["assistant-input"], "role": "model"},
                {"parts": ["generic-input"], "role": "user"},
            ],
            stream=True,
            generation_config=GenerationConfig(
                max_output_tokens=997, temperature=0.1, top_p=0.5, top_k=50, stop_sequences=["<|Response|>"]
            ),
        )
        assert text_artifact.value == "model-output"

    def test_prompt_stack_to_model_input(self):
        # Given
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")
        prompt_stack = PromptStack()
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_assistant_input("assistant-input")
        prompt_stack.add_user_input("user-input")

        # When
        model_input = driver._prompt_stack_to_model_input(prompt_stack)

        # Then
        assert model_input == [
            {"role": "user", "parts": ["system-input", "user-input"]},
            {"role": "model", "parts": ["assistant-input"]},
            {"role": "user", "parts": ["generic-input"]},
            {"role": "model", "parts": ["assistant-input"]},
            {"role": "user", "parts": ["user-input"]},
        ]

    def test_to_content_dict(self):
        # Given
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")

        # When
        assert driver._GooglePromptDriver__to_content_dict(PromptStack.Input("system-input", "system")) == {
            "role": "user",
            "parts": ["system-input"],
        }
        assert driver._GooglePromptDriver__to_content_dict(PromptStack.Input("user-input", "user")) == {
            "role": "user",
            "parts": ["user-input"],
        }
        assert driver._GooglePromptDriver__to_content_dict(PromptStack.Input("assistant-input", "assistant")) == {
            "role": "model",
            "parts": ["assistant-input"],
        }

        assert driver._GooglePromptDriver__to_content_dict(PromptStack.Input("generic-input", "generic")) == {
            "role": "user",
            "parts": ["generic-input"],
        }
