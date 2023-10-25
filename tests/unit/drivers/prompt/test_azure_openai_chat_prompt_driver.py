from griptape.drivers import AzureOpenAiChatPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import (
    TestOpenAiChatPromptDriverFixtureMixin,
)


class TestAzureOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert AzureOpenAiChatPromptDriver(
            api_base="foobar", deployment_id="foobar", model="gpt-4"
        )

    def test_try_run(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            api_base="api-base", deployment_id="deployment-id", model="gpt-4"
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            messages=messages,
            deployment_id="deployment-id",
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(
        self, mock_chat_completion_stream_create, prompt_stack, messages
    ):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            api_base="api-base",
            deployment_id="deployment-id",
            model="gpt-4",
            stream=True,
        )

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            stream=True,
            messages=messages,
            deployment_id="deployment-id",
        )
        assert text_artifact.value == "model-output"
