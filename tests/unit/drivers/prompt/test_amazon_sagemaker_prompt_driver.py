import boto3
from griptape.drivers import AmazonSageMakerPromptDriver
from griptape.drivers import SageMakerLlamaPromptModelDriver
from griptape.tokenizers import OpenAiTokenizer, HuggingFaceTokenizer


class TestAmazonSageMakerPromptDriver:
    def test_init(self):
        assert AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=SageMakerLlamaPromptModelDriver()
        )

    def test_custom_tokenizer(self):
        assert isinstance(AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=SageMakerLlamaPromptModelDriver()
        ).tokenizer, HuggingFaceTokenizer)

        assert isinstance(AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=OpenAiTokenizer(),
            prompt_model_driver=SageMakerLlamaPromptModelDriver()
        ).tokenizer, OpenAiTokenizer)
