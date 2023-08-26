import boto3
from griptape.drivers import AmazonSagemakerPromptDriver
from griptape.drivers import SagemakerLlamaPromptModelDriver
from griptape.tokenizers import TiktokenTokenizer, HuggingFaceTokenizer


class TestAmazonSagemakerPromptDriver:
    def test_init(self):
        assert AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver_class=SagemakerLlamaPromptModelDriver
        )

    def test_custom_tokenizer(self):
        assert isinstance(AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver_class=SagemakerLlamaPromptModelDriver
        ).tokenizer, HuggingFaceTokenizer)

        assert isinstance(AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_driver_class=SagemakerLlamaPromptModelDriver
        ).tokenizer, TiktokenTokenizer)
