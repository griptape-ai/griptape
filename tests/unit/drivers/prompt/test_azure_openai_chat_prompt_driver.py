import pytest
from unittest.mock import Mock
from griptape.drivers import AzureOpenAiChatPromptDriver
from griptape.common import TextDeltaMessageContent
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestAzureOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    @pytest.fixture
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.create
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[Mock(message=Mock(content="model-output"))],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )
        return mock_chat_create

    @pytest.fixture
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.create
        mock_chat_create.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="model-output"))], usage=None),
                Mock(choices=None, usage=Mock(prompt_tokens=5, completion_tokens=10)),
            ]
        )
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
            model=driver.model, temperature=driver.temperature, user=driver.user, messages=messages
        )
        assert text_artifact.value == "model-output"
        assert text_artifact.usage.input_tokens == 5
        assert text_artifact.usage.output_tokens == 10

    def test_try_stream_run(self, mock_chat_completion_stream_create, prompt_stack, messages):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            azure_endpoint="endpoint", azure_deployment="deployment-id", model="gpt-4", stream=True
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            stream=True,
            messages=messages,
            stream_options={"include_usage": True},
        )

        assert isinstance(event, TextDeltaMessageContent)
        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
