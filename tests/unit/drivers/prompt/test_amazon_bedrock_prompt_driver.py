import boto3
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.drivers import BedrockClaudePromptModelDriver, BedrockTitanPromptModelDriver
from griptape.tokenizers import AnthropicTokenizer, AmazonBedrockTokenizer


class TestAmazonBedrockPromptDriver:
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
