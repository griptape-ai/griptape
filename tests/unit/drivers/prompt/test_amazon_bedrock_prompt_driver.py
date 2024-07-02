import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.common import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver


class TestAmazonBedrockPromptDriver:
    @pytest.fixture
    def mock_converse(self, mocker):
        mock_converse = mocker.patch("boto3.Session").return_value.client.return_value.converse

        mock_converse.return_value = {
            "output": {"message": {"content": [{"text": "model-output"}]}},
            "usage": {"inputTokens": 5, "outputTokens": 10},
        }

        return mock_converse

    @pytest.fixture
    def mock_converse_stream(self, mocker):
        mock_converse_stream = mocker.patch("boto3.Session").return_value.client.return_value.converse_stream

        mock_converse_stream.return_value = {
            "stream": [
                {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "model-output"}}},
                {"metadata": {"usage": {"inputTokens": 5, "outputTokens": 10}}},
            ]
        }

        return mock_converse_stream

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        if request.param:
            prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(TextArtifact("user-input"))
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        prompt_stack.add_assistant_message("assistant-input")

        return prompt_stack

    @pytest.fixture
    def messages(self):
        return [
            {"role": "user", "content": [{"text": "user-input"}]},
            {"role": "user", "content": [{"text": "user-input"}]},
            {"role": "user", "content": [{"image": {"format": "png", "source": {"bytes": b"image-data"}}}]},
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
            messages=messages,
            **({"system": [{"text": "system-input"}]} if prompt_stack.system_messages else {"system": []}),
            inferenceConfig={"temperature": driver.temperature},
            additionalModelRequestFields={},
        )
        assert text_artifact.value == "model-output"
        assert text_artifact.usage.input_tokens == 5
        assert text_artifact.usage.output_tokens == 10

    def test_try_stream_run(self, mock_converse_stream, prompt_stack, messages):
        # Given
        driver = AmazonBedrockPromptDriver(model="ai21.j2", stream=True)

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_converse_stream.assert_called_once_with(
            modelId=driver.model,
            messages=messages,
            **({"system": [{"text": "system-input"}]} if prompt_stack.system_messages else {"system": []}),
            inferenceConfig={"temperature": driver.temperature},
            additionalModelRequestFields={},
        )

        assert event.content.text == "model-output"

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
