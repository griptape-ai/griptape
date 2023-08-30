import boto3
from griptape.drivers import AmazonSageMakerPromptDriver
from griptape.drivers import SageMakerLlamaPromptModelDriver
from griptape.tokenizers import TiktokenTokenizer, HuggingFaceTokenizer


class TestAmazonSageMakerPromptDriver:
    def test_init(self):
        assert AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver_type=SageMakerLlamaPromptModelDriver
        )

    def test_custom_tokenizer(self):
        assert isinstance(AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver_type=SageMakerLlamaPromptModelDriver
        ).tokenizer, HuggingFaceTokenizer)

        assert isinstance(AmazonSageMakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_driver_type=SageMakerLlamaPromptModelDriver
        ).tokenizer, TiktokenTokenizer)
