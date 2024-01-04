import boto3
import pytest
from griptape.drivers import AmazonSageMakerEmbeddingDriver, SageMakerHuggingFaceEmbeddingModelDriver
from tests.mocks.mock_tokenizer import MockTokenizer


class TestSageMakerHuggingFaceEmbeddingModelDriver:
    @pytest.fixture
    def driver(self):
        return AmazonSageMakerEmbeddingDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=MockTokenizer(model="foo"),
            embedding_model_driver=SageMakerHuggingFaceEmbeddingModelDriver(),
        ).embedding_model_driver

    def test_chunk_to_model_params(self, driver):
        assert driver.chunk_to_model_params("foobar")["text_inputs"] == "foobar"

    def test_process_output(self, driver):
        assert driver.process_output({"embedding": [["foobar"]]}) == ["foobar"]
