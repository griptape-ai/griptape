import pytest
from unittest import mock
from griptape.drivers import AmazonSagemakerEmbeddingDriver
from griptape.tokenizers.openai_tokenizer import OpenAiTokenizer


class TestAmazonSagemakerEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_embeddings = '{"embedding": [[0, 1, 0]]}'.encode("utf-8")
        mock_session_class = mocker.patch("boto3.Session")
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_embeddings
        mock_client.invoke_endpoint.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_init(self):
        assert AmazonSagemakerEmbeddingDriver(
            endpoint="test-endpoint",
            dimensions=4096,
            tokenizer=OpenAiTokenizer(
                model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL
            ),
        )

    def test_try_embed_chunk(self):
        assert AmazonSagemakerEmbeddingDriver(
            endpoint="test-endpoint",
            dimensions=4096,
            tokenizer=OpenAiTokenizer(
                model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL
            ),
        ).try_embed_chunk("foobar") == [0, 1, 0]
