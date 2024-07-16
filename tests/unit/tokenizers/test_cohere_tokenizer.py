import cohere
import pytest

from griptape.tokenizers import CohereTokenizer


class TestCohereTokenizer:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value.tokenize.return_value.tokens = ["foo", "bar"]

        return mock_client

    @pytest.fixture()
    def tokenizer(self):
        return CohereTokenizer(model="command", client=cohere.Client("foobar"))

    def test_init(self, tokenizer):
        assert tokenizer

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar") == 4094

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar") == 4094
