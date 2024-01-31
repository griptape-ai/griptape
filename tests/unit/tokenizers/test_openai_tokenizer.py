import pytest
from griptape.tokenizers import OpenAiTokenizer


class TestOpenAiTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

    @pytest.fixture
    def tokenizer_32k(self):
        return OpenAiTokenizer(model="gpt-4-32k")

    def test_token_count_for_text(self, tokenizer):
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_initialize_with_unknown_model(self):
        tokenizer = OpenAiTokenizer(model="not-a-real-model")
        assert tokenizer.max_tokens == OpenAiTokenizer.DEFAULT_MAX_TOKENS - OpenAiTokenizer.TOKEN_OFFSET

    def test_token_count_for_messages(self, tokenizer):
        assert (
            tokenizer.count_tokens(
                [{"role": "system", "content": "foobar baz"}, {"role": "user", "content": "how foobar am I?"}],
                model="gpt-4",
            )
            == 19
        )

        assert (
            tokenizer.count_tokens(
                [{"role": "system", "content": "foobar baz"}, {"role": "user", "content": "how foobar am I?"}],
                model="gpt-3.5-turbo-0301",
            )
            == 21
        )

        assert (
            tokenizer.count_tokens(
                [{"role": "system", "content": "foobar baz"}, {"role": "user", "content": "how foobar am I?"}],
                model="gpt-35-turbo",
            )
            == 19
        )

    def test_tokens_left(self, tokenizer):
        assert tokenizer.count_tokens_left("foo bar huzzah") == 4083

    def test_tokens_left_32k(self, tokenizer_32k):
        assert tokenizer_32k.count_tokens_left("foo bar huzzah") == 32755
