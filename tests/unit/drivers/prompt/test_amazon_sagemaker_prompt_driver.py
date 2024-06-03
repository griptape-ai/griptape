from botocore.response import StreamingBody
from griptape.artifacts import TextArtifact
from griptape.drivers import AmazonSageMakerPromptDriver, SageMakerLlamaPromptModelDriver
from griptape.tokenizers import HuggingFaceTokenizer, OpenAiTokenizer
from griptape.utils import PromptStack
from io import BytesIO
from unittest.mock import Mock
import json
import pytest


class TestAmazonSageMakerPromptDriver:
    @pytest.fixture
    def mock_model_driver(self):
        mock_model_driver = Mock()
        mock_model_driver.prompt_stack_to_model_input.return_value = "model-inputs"
        mock_model_driver.prompt_stack_to_model_params.return_value = "model-params"
        mock_model_driver.process_output.return_value = TextArtifact("model-output")
        return mock_model_driver

    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        return mocker.patch("boto3.Session").return_value.client.return_value

    def test_init(self):
        assert AmazonSageMakerPromptDriver(endpoint="foo", prompt_model_driver=SageMakerLlamaPromptModelDriver())

    def test_custom_tokenizer(self):
        assert isinstance(
            AmazonSageMakerPromptDriver(
                endpoint="foo", prompt_model_driver=SageMakerLlamaPromptModelDriver()
            ).tokenizer,
            HuggingFaceTokenizer,
        )

        assert isinstance(
            AmazonSageMakerPromptDriver(
                endpoint="foo",
                tokenizer=OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL),
                prompt_model_driver=SageMakerLlamaPromptModelDriver(),
            ).tokenizer,
            OpenAiTokenizer,
        )

    def test_try_run(self, mock_model_driver, mock_client):
        # Given
        driver = AmazonSageMakerPromptDriver(endpoint="model", prompt_model_driver=mock_model_driver)
        prompt_stack = PromptStack()
        prompt_stack.add_user_input("prompt-stack")
        response_body = "invoke-endpoint-response-body"
        mock_client.invoke_endpoint.return_value = {"Body": to_streaming_body(response_body)}

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_model_driver.prompt_stack_to_model_input.assert_called_once_with(prompt_stack)
        mock_model_driver.prompt_stack_to_model_params.assert_called_once_with(prompt_stack)
        mock_client.invoke_endpoint.assert_called_once_with(
            EndpointName=driver.endpoint,
            ContentType="application/json",
            Body=json.dumps(
                {
                    "inputs": mock_model_driver.prompt_stack_to_model_input.return_value,
                    "parameters": mock_model_driver.prompt_stack_to_model_params.return_value,
                }
            ),
            CustomAttributes="accept_eula=true",
        )
        mock_model_driver.process_output.assert_called_once_with(response_body)
        assert text_artifact == mock_model_driver.process_output.return_value

    def test_try_run_throws_on_empty_response(self, mock_model_driver, mock_client):
        # Given
        driver = AmazonSageMakerPromptDriver(endpoint="model", prompt_model_driver=mock_model_driver)
        mock_client.invoke_endpoint.return_value = {"Body": to_streaming_body("")}
        prompt_stack = PromptStack()
        prompt_stack.add_user_input("prompt-stack")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "model response is empty"


def to_streaming_body(text: str) -> StreamingBody:
    bytes = json.dumps(text).encode("utf-8")
    return StreamingBody(BytesIO(bytes), len(bytes))
