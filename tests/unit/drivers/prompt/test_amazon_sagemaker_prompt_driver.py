import boto3
from griptape.drivers import AmazonSagemakerPromptDriver
from griptape.prompt_model_adapters import LlamaPromptModelAdapter
from griptape.tokenizers import TiktokenTokenizer


class TestAmazonSagemakerPromptDriver:
    def test_init(self):
        assert AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_driver_class=LlamaPromptModelAdapter
        )
