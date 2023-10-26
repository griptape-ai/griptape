import pytest
from griptape.tokenizers import OpenAiTokenizer


class TestOpenAiTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return OpenAiTokenizer(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL
        )

    @pytest.fixture
    def tokenizer_32k(self):
        return OpenAiTokenizer(model="gpt-4-32k")

    def test_encode(self, tokenizer):
        assert tokenizer.encode("foo bar") == [8134, 3703]

    def test_decode(self, tokenizer):
        assert tokenizer.decode([8134, 3703]) == "foo bar"

    def test_token_count_for_text(self, tokenizer):
        assert tokenizer.token_count("foo bar huzzah") == 5

    def test_token_count_for_messages(self, tokenizer):
        assert (
            tokenizer.token_count(
                [
                    {"role": "system", "content": "foobar baz"},
                    {"role": "user", "content": "how foobar am I?"},
                ],
                model="gpt-4",
            )
            == 19
        )

        assert (
            tokenizer.token_count(
                [
                    {"role": "system", "content": "foobar baz"},
                    {"role": "user", "content": "how foobar am I?"},
                ],
                model="gpt-3.5-turbo-0301",
            )
            == 21
        )

        assert (
            tokenizer.token_count(
                [
                    {"role": "system", "content": "foobar baz"},
                    {"role": "user", "content": "how foobar am I?"},
                ],
                model="gpt-35-turbo",
            )
            == 19
        )

    def test_tokens_left(self, tokenizer):
        assert tokenizer.tokens_left("foo bar huzzah") == 4083

    def test_tokens_left_32k(self, tokenizer_32k):
        assert tokenizer_32k.tokens_left("foo bar huzzah") == 32755

    def test_encoding(self, tokenizer):
        assert tokenizer.encoding.name == "cl100k_base"

    def test_chunk_tokens(self, tokenizer):
        tokens = tokenizer.encode("foo bar")

        assert [chunk for chunk in tokenizer.chunk_tokens(tokens)] == [
            (8134, 3703)
        ]
