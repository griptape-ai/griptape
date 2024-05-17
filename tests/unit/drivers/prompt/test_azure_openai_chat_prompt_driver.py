import pytest
from unittest.mock import Mock
from griptape.drivers import AzureOpenAiChatPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestAzureOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.with_raw_response.create
        mock_choice = Mock()
        mock_choice.message.content = "model-output"
        mock_choice.message.tool_calls = None
        mock_chat_create.return_value.headers = {}
        mock_chat_create.return_value.parse.return_value.choices = [mock_choice]
        return mock_chat_create

    @pytest.fixture
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.create
        mock_chunk = Mock()
        mock_choice = Mock()
        mock_choice.delta.content = "model-output"
        mock_choice.delta.tool_calls = None
        mock_chunk.choices = [mock_choice]
        mock_chat_create.return_value = iter([mock_chunk])
        return mock_chat_create

    def test_init(self):
        assert AzureOpenAiChatPromptDriver(azure_endpoint="foobar", azure_deployment="foobar", model="gpt-4")
        assert AzureOpenAiChatPromptDriver(azure_endpoint="foobar", model="gpt-4").azure_deployment == "gpt-4"

    def test_try_run(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = AzureOpenAiChatPromptDriver(azure_endpoint="endpoint", azure_deployment="deployment-id", model="gpt-4")

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            messages=messages,
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_chat_completion_stream_create, prompt_stack, messages):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            azure_endpoint="endpoint", azure_deployment="deployment-id", model="gpt-4", stream=True
        )

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            stream=True,
            messages=messages,
        )
        assert text_artifact.value == "model-output"
