from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.common import PromptStack
import pytest


class TestHuggingFaceHubPromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("huggingface_hub.InferenceClient").return_value
        mock_client.text_generation.return_value = "model-output"
        return mock_client

    @pytest.fixture
    def mock_client_stream(self, mocker):
        mock_client = mocker.patch("huggingface_hub.InferenceClient").return_value
        mock_client.text_generation.return_value = iter(["model-output"])

        return mock_client

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        return prompt_stack

    @pytest.fixture(autouse=True)
    def mock_autotokenizer(self, mocker):
        mock_autotokenizer = mocker.patch("transformers.AutoTokenizer.from_pretrained").return_value
        mock_autotokenizer.model_max_length = 42
        return mock_autotokenizer

    def test_init(self):
        assert HuggingFaceHubPromptDriver(api_token="foobar", model="gpt2")

    def test_try_run(self, prompt_stack, mock_client):
        # Given
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        assert text_artifact.value == "model-output"

    def test_try_stream(self, prompt_stack, mock_client_stream):
        # Given
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        assert text_artifact.value == "model-output"
