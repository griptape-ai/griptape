import pytest

from griptape.tokenizers.grok_tokenizer import GrokTokenizer


class TestGrokTokenizer:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "token_ids": [
                {"token_id": 13902, "string_token": "Hello", "token_bytes": [72, 101, 108, 108, 111]},
                {"token_id": 1749, "string_token": " world", "token_bytes": [32, 119, 111, 114, 108, 100]},
                {"token_id": 161, "string_token": "!", "token_bytes": [33]},
            ]
        }

        return mock_post

    @pytest.fixture()
    def tokenizer(self):
        return GrokTokenizer(model="grok-2-latest", api_key="foobar")

    def test_init(self, tokenizer):
        assert tokenizer

    def test_count_tokens(self, tokenizer):
        assert tokenizer.count_tokens("Hello world!") == 3

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar") == 131069

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar") == 4093
