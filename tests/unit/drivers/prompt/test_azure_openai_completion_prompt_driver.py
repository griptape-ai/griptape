from griptape.drivers import AzureOpenAiCompletionPromptDriver
from tests.unit.drivers.prompt.test_openai_completion_prompt_driver import (
    TestOpenAiCompletionPromptDriverFixtureMixin,
)
from unittest.mock import ANY


class TestAzureOpenAiCompletionPromptDriver(
    TestOpenAiCompletionPromptDriverFixtureMixin
):
    def test_init(self):
        assert AzureOpenAiCompletionPromptDriver(
            api_base="foobar", deployment_id="foobar", model="text-davinci-003"
        )

    def test_try_run(self, mock_completion_create, prompt_stack, prompt):
        # Given
        driver = AzureOpenAiCompletionPromptDriver(
            api_base="api-base",
            deployment_id="deployment-id",
            model="text-davinci-003",
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
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            prompt=prompt,
            deployment_id="deployment-id",
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(
        self, mock_completion_stream_create, prompt_stack, prompt
    ):
        # Given
        driver = AzureOpenAiCompletionPromptDriver(
            api_base="api-base",
            deployment_id="deployment-id",
            model="text-davinci-003",
            stream=True,
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
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            stream=driver.stream,
            prompt=prompt,
            deployment_id="deployment-id",
        )
        assert text_artifact.value == "model-output"
