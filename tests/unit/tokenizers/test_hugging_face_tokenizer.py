from os import environ

environ["TRANSFORMERS_VERBOSITY"] = "error"

import pytest

from griptape.tokenizers import HuggingFaceTokenizer


class TestHuggingFaceTokenizer:
    @pytest.fixture(autouse=True)
    def mock_tokenizer(self, mocker):
        from_pretrained = tokenizer = mocker.patch("transformers.AutoTokenizer").from_pretrained
        from_pretrained.return_value.apply_chat_template.return_value = [1, 2, 3]
        from_pretrained.return_value.decode.return_value = "foo\n\nUser: bar"
        from_pretrained.return_value.encode.return_value = [1, 2, 3]

        return tokenizer

    @pytest.fixture()
    def tokenizer(self):
        return HuggingFaceTokenizer(model="foo", max_input_tokens=1024, max_output_tokens=1024)

    def test_token_count(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 3

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == 1021

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == 1021
