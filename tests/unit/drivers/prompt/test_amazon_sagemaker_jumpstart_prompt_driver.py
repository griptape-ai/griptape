import json
from io import BytesIO
from typing import Any

import pytest
from botocore.response import StreamingBody

from griptape.common import PromptStack
from griptape.drivers.prompt.amazon_sagemaker_jumpstart_prompt_driver import AmazonSageMakerJumpstartPromptDriver
from griptape.tokenizers import HuggingFaceTokenizer


def to_streaming_body(data: Any) -> StreamingBody:
    encoded_body = json.dumps(data).encode("utf-8")

    return StreamingBody(BytesIO(encoded_body), len(encoded_body))


class TestAmazonSageMakerJumpstartPromptDriver:
    @pytest.fixture(autouse=True)
    def tokenizer(self, mocker):
        from_pretrained = mocker.patch("transformers.AutoTokenizer").from_pretrained
        from_pretrained.return_value.decode.return_value = "foo\n\nUser: bar"
        from_pretrained.return_value.apply_chat_template.return_value = [1, 2, 3]
        from_pretrained.return_value.encode.return_value = [1, 2, 3]
        from_pretrained.return_value.model_max_length = 8000
        from_pretrained.return_value.eos_token_id = 1

        return from_pretrained

    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        return mocker.patch("boto3.Session").return_value.client.return_value

    def test_init(self):
        assert AmazonSageMakerJumpstartPromptDriver(endpoint="foo", model="bar")

    def test_try_run(self, mock_client):
        # Given
        driver = AmazonSageMakerJumpstartPromptDriver(endpoint="model", model="model")
        prompt_stack = PromptStack()
        prompt_stack.add_user_message("prompt-stack")

        # When
        response_body = [{"generated_text": "foobar"}]
        mock_client.invoke_endpoint.return_value = {"Body": to_streaming_body(response_body)}
        text_artifact = driver.try_run(prompt_stack)
        assert isinstance(driver.tokenizer, HuggingFaceTokenizer)

        # Then
        mock_client.invoke_endpoint.assert_called_with(
            EndpointName=driver.endpoint,
            ContentType="application/json",
            Body=json.dumps(
                {
                    "inputs": "foo\n\nUser: bar",
                    "parameters": {
                        "temperature": driver.temperature,
                        "max_new_tokens": 250,
                        "do_sample": True,
                        "eos_token_id": 1,
                        "stop_strings": [],
                        "return_full_text": False,
                    },
                }
            ),
            CustomAttributes="accept_eula=true",
        )

        assert text_artifact.value == "foobar"
        assert text_artifact.usage.input_tokens == 3
        assert text_artifact.usage.output_tokens == 3

        # When
        response_body = {"generated_text": "foobar"}
        mock_client.invoke_endpoint.return_value = {"Body": to_streaming_body(response_body)}
        text_artifact = driver.try_run(prompt_stack)
        assert isinstance(driver.tokenizer, HuggingFaceTokenizer)

        # Then
        mock_client.invoke_endpoint.assert_called_with(
            EndpointName=driver.endpoint,
            ContentType="application/json",
            Body=json.dumps(
                {
                    "inputs": "foo\n\nUser: bar",
                    "parameters": {
                        "temperature": driver.temperature,
                        "max_new_tokens": 250,
                        "do_sample": True,
                        "eos_token_id": 1,
                        "stop_strings": [],
                        "return_full_text": False,
                    },
                }
            ),
            CustomAttributes="accept_eula=true",
        )

        assert text_artifact.value == "foobar"

    def test_try_stream(self, mock_client):
        # Given
        driver = AmazonSageMakerJumpstartPromptDriver(endpoint="model", model="model")
        prompt_stack = PromptStack()
        prompt_stack.add_user_message("prompt-stack")

        # When
        with pytest.raises(NotImplementedError) as e:
            driver.try_stream(prompt_stack)

        # Then
        assert e.value.args[0] == "streaming is not supported"

    def test_stream_init(self):
        # Given
        driver = AmazonSageMakerJumpstartPromptDriver(endpoint="model", model="model")

        # When
        with pytest.raises(ValueError) as e:
            driver.stream = True

        # Then
        assert e.value.args[0] == "streaming is not supported"

    def test_try_run_throws_on_empty_response(self, mock_client):
        # Given
        driver = AmazonSageMakerJumpstartPromptDriver(endpoint="model", model="model")
        mock_client.invoke_endpoint.return_value = {"Body": to_streaming_body([])}
        prompt_stack = PromptStack()
        prompt_stack.add_user_message("prompt-stack")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "model response is empty"
