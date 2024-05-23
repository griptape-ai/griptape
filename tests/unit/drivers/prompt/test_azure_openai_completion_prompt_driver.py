import pytest
from unittest.mock import Mock
from griptape.drivers import AzureOpenAiCompletionPromptDriver
from tests.unit.drivers.prompt.test_openai_completion_prompt_driver import TestOpenAiCompletionPromptDriverFixtureMixin
from unittest.mock import ANY


class TestAzureOpenAiCompletionPromptDriver(TestOpenAiCompletionPromptDriverFixtureMixin):
    @pytest.fixture
    def mock_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.completions.create
        mock_choice = Mock()
        mock_choice.text = "model-output"
        mock_chat_create.return_value.choices = [mock_choice]
        return mock_chat_create

    @pytest.fixture
    def mock_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.completions.create
        mock_chunk = Mock()
        mock_choice = Mock()
        mock_choice.text = "model-output"
        mock_chunk.choices = [mock_choice]
        mock_chat_create.return_value = iter([mock_chunk])
        return mock_chat_create

    def test_init(self):
        assert AzureOpenAiCompletionPromptDriver(
            azure_endpoint="endpoint", azure_deployment="deployment", model="text-davinci-003"
        )
        assert (
            AzureOpenAiCompletionPromptDriver(azure_endpoint="endpoint", model="text-davinci-003").azure_deployment
            == "text-davinci-003"
        )

    def test_try_run(self, mock_completion_create, prompt_stack, prompt):
        # Given
        driver = AzureOpenAiCompletionPromptDriver(
            azure_endpoint="endpoint", azure_deployment="deployment", model="text-davinci-003"
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_completion_create.assert_called_once_with(
            model=driver.model,
            max_tokens=ANY,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            prompt=prompt,
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_completion_stream_create, prompt_stack, prompt):
        # Given
        driver = AzureOpenAiCompletionPromptDriver(
            azure_endpoint="endpoint", azure_deployment="deployment", model="text-davinci-003", stream=True
        )

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_completion_stream_create.assert_called_once_with(
            model=driver.model,
            max_tokens=ANY,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            stream=True,
            prompt=prompt,
        )
        assert text_artifact.value == "model-output"
