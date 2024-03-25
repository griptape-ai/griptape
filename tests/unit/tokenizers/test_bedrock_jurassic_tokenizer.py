import pytest
from unittest import mock
from griptape.tokenizers import BedrockJurassicTokenizer


class TestBedrockJurassicTokenizer:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_tokenization = '{"prompt": {"tokens": [{}, {}, {}]}}'
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_tokenization
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    @pytest.fixture
    def tokenizer(self, request):
        return BedrockJurassicTokenizer(model=request.param)

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [("ai21.j2-mid-v1", 8186), ("ai21.j2-ultra-v1", 8186), ("ai21.j2-large-v1", 8186), ("ai21.j2-large-v2", 8186)],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("System: foo\nUser: bar\nAssistant:") == expected

    @pytest.mark.parametrize(
        "tokenizer,expected",
        [("ai21.j2-mid-v1", 8185), ("ai21.j2-ultra-v1", 8185), ("ai21.j2-large-v1", 8185), ("ai21.j2-large-v2", 2042)],
        indirect=["tokenizer"],
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("System: foo\nUser: bar\nAssistant:") == expected
