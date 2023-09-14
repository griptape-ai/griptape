from unittest import mock
import pytest
import boto3
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.drivers import BedrockClaudePromptModelDriver, BedrockTitanPromptModelDriver
from griptape.tokenizers import AnthropicTokenizer, AmazonBedrockTokenizer


class TestAmazonBedrockPromptDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_init(self):
        assert AmazonBedrockPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockClaudePromptModelDriver()
        )

    def test_custom_tokenizer(self):
        assert isinstance(AmazonBedrockPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockClaudePromptModelDriver()
        ).tokenizer, AnthropicTokenizer)

        assert isinstance(AmazonBedrockPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=AmazonBedrockTokenizer(),
            prompt_model_driver=BedrockTitanPromptModelDriver()
        ).tokenizer, AmazonBedrockTokenizer)
