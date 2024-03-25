from botocore.response import StreamingBody
from griptape.artifacts import TextArtifact
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.drivers import BedrockClaudePromptModelDriver, BedrockTitanPromptModelDriver
from griptape.tokenizers import AnthropicTokenizer, BedrockTitanTokenizer
from io import StringIO
from unittest.mock import Mock
import json
import pytest


class TestAmazonBedrockPromptDriver:
    @pytest.fixture
    def mock_prompt_model_driver(self):
        mock_prompt_model_driver = Mock()
        mock_prompt_model_driver.prompt_stack_to_model_params.return_value = {"model-param-key": "model-param-value"}
        mock_prompt_model_driver.process_output.return_value = TextArtifact("model-output")
        return mock_prompt_model_driver

    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        return mocker.patch("boto3.Session").return_value.client.return_value

    def test_init(self):
        assert AmazonBedrockPromptDriver(model="anthropic.claude", prompt_model_driver=BedrockClaudePromptModelDriver())

    def test_custom_tokenizer(self):
        assert isinstance(
            AmazonBedrockPromptDriver(
                model="anthropic.claude", prompt_model_driver=BedrockClaudePromptModelDriver()
            ).tokenizer,
            AnthropicTokenizer,
        )

        assert isinstance(
            AmazonBedrockPromptDriver(
                model="titan",
                tokenizer=BedrockTitanTokenizer(model="amazon"),
                prompt_model_driver=BedrockTitanPromptModelDriver(),
            ).tokenizer,
            BedrockTitanTokenizer,
        )

    @pytest.mark.parametrize("model_inputs", [{"model-input-key": "model-input-value"}, "not-a-dict"])
    def test_try_run(self, model_inputs, mock_prompt_model_driver, mock_client):
        # Given
        driver = AmazonBedrockPromptDriver(model="model", prompt_model_driver=mock_prompt_model_driver)
        prompt_stack = "prompt-stack"
        response_body = "invoke-model-response-body"
        mock_prompt_model_driver.prompt_stack_to_model_input.return_value = model_inputs
        mock_client.invoke_model.return_value = {"body": to_streaming_body(response_body)}

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_prompt_model_driver.prompt_stack_to_model_input.assert_called_once_with(prompt_stack)
        mock_prompt_model_driver.prompt_stack_to_model_params.assert_called_once_with(prompt_stack)
        mock_client.invoke_model.assert_called_once_with(
            modelId=driver.model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    **mock_prompt_model_driver.prompt_stack_to_model_params.return_value,
                    **(model_inputs if isinstance(model_inputs, dict) else {}),
                }
            ),
        )
        mock_prompt_model_driver.process_output.assert_called_once_with(response_body)
        assert text_artifact == mock_prompt_model_driver.process_output.return_value

    @pytest.mark.parametrize("model_inputs", [{"model-input-key": "model-input-value"}, "not-a-dict"])
    def test_try_stream_run(self, model_inputs, mock_prompt_model_driver, mock_client):
        # Given
        driver = AmazonBedrockPromptDriver(model="model", prompt_model_driver=mock_prompt_model_driver, stream=True)
        prompt_stack = "prompt-stack"
        model_response = "invoke-model-response-body"
        response_body = [{"chunk": {"bytes": model_response}}]
        mock_prompt_model_driver.prompt_stack_to_model_input.return_value = model_inputs
        mock_client.invoke_model_with_response_stream.return_value = {"body": response_body}

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_prompt_model_driver.prompt_stack_to_model_input.assert_called_once_with(prompt_stack)
        mock_prompt_model_driver.prompt_stack_to_model_params.assert_called_once_with(prompt_stack)
        mock_client.invoke_model_with_response_stream.assert_called_once_with(
            modelId=driver.model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    **mock_prompt_model_driver.prompt_stack_to_model_params.return_value,
                    **(model_inputs if isinstance(model_inputs, dict) else {}),
                }
            ),
        )
        mock_prompt_model_driver.process_output.assert_called_once_with(model_response)
        assert text_artifact.value == mock_prompt_model_driver.process_output.return_value.value

    def test_try_run_throws_on_empty_response(self, mock_prompt_model_driver, mock_client):
        # Given
        driver = AmazonBedrockPromptDriver(model="model", prompt_model_driver=mock_prompt_model_driver)
        mock_client.invoke_model.return_value = {"body": to_streaming_body("")}

        # When
        with pytest.raises(Exception) as e:
            driver.try_run("prompt-stack")

        # Then
        assert e.value.args[0] == "model response is empty"


def to_streaming_body(text: str) -> StreamingBody:
    return StreamingBody(StringIO(text), len(text))
