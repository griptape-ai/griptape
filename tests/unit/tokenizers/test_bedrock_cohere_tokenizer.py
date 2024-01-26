import pytest
from unittest import mock
from griptape.tokenizers import BedrockCohereTokenizer


class TestBedrockCohereTokenizer:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_tokenization = '{"inputTextTokenCount": 2}'
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_tokenization
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    def test_cohere_tokens_left(self):
        assert BedrockCohereTokenizer().count_tokens_left("foo bar") == 510
