import pytest

from griptape.common import PromptStack
from griptape.common.prompt_stack.contents.delta_text_prompt_stack_content import DeltaTextPromptStackContent
from griptape.drivers import AmazonBedrockPromptDriver


class TestAmazonBedrockPromptDriver:
    @pytest.fixture
    def mock_converse(self, mocker):
        mock_converse = mocker.patch("boto3.Session").return_value.client.return_value.converse

        mock_converse.return_value = {
            "output": {"message": {"content": [{"text": "model-output"}]}},
            "usage": {"inputTokens": 100, "outputTokens": 100},
        }

        return mock_converse

    @pytest.fixture
    def mock_converse_stream(self, mocker):
        mock_converse_stream = mocker.patch("boto3.Session").return_value.client.return_value.converse_stream

        mock_converse_stream.return_value = {
            "stream": [{"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "model-output"}}}]
        }

        return mock_converse_stream

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_assistant_message("assistant-input")

        return prompt_stack

    @pytest.fixture
    def messages(self):
        return [
            {"role": "system", "content": [{"text": "system-input"}]},
            {"role": "user", "content": [{"text": "user-input"}]},
            {"role": "assistant", "content": [{"text": "assistant-input"}]},
        ]

    def test_try_run(self, mock_converse, prompt_stack, messages):
        # Given
        driver = AmazonBedrockPromptDriver(model="ai21.j2")

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_converse.assert_called_once_with(
            modelId=driver.model,
            messages=[
                {"role": "user", "content": [{"text": "user-input"}]},
                {"role": "assistant", "content": [{"text": "assistant-input"}]},
            ],
            system=[{"text": "system-input"}],
            inferenceConfig={"temperature": driver.temperature},
            additionalModelRequestFields={},
        )
        assert text_artifact.value == "model-output"

    def test_try_stream_run(self, mock_converse_stream, prompt_stack, messages):
        # Given
        driver = AmazonBedrockPromptDriver(model="ai21.j2", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_converse_stream.assert_called_once_with(
            modelId=driver.model,
            messages=[
                {"role": "user", "content": [{"text": "user-input"}]},
                {"role": "assistant", "content": [{"text": "assistant-input"}]},
            ],
            system=[{"text": "system-input"}],
            inferenceConfig={"temperature": driver.temperature},
            additionalModelRequestFields={},
        )

        if isinstance(text_artifact, DeltaTextPromptStackContent):
            assert text_artifact.text == "model-output"
