import pytest

from griptape.tokenizers import OpenAiTokenizer


class TestOpenAiTokenizer:
    @pytest.fixture()
    def tokenizer(self, request):
        return OpenAiTokenizer(model=request.param)

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("gpt-4-1106", 5),
            ("gpt-4-32k", 5),
            ("gpt-4", 5),
            ("gpt-4o", 5),
            ("gpt-3.5-turbo-0301", 5),
            ("gpt-3.5-turbo-16k", 5),
            ("gpt-3.5-turbo", 5),
            ("gpt-35-turbo-16k", 5),
            ("gpt-35-turbo", 5),
            ("text-embedding-ada-002", 5),
            ("text-embedding-ada-001", 5),
            ("text-embedding-3-small", 5),
            ("text-embedding-3-large", 5),
        ],
        indirect=["tokenizer"],
    )
    def test_token_count_for_text(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    def test_initialize_with_unknown_model(self):
        tokenizer = OpenAiTokenizer(model="not-a-real-model")
        assert tokenizer.max_input_tokens == OpenAiTokenizer.DEFAULT_MAX_TOKENS - OpenAiTokenizer.TOKEN_OFFSET

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("gpt-4-1106", 19),
            ("gpt-4-32k", 19),
            ("gpt-4", 19),
            ("gpt-4o", 19),
            ("gpt-3.5-turbo-0301", 21),
            ("gpt-3.5-turbo-16k", 19),
            ("gpt-3.5-turbo", 19),
            ("gpt-35-turbo-16k", 19),
            ("gpt-35-turbo", 19),
        ],
        indirect=["tokenizer"],
    )
    def test_token_count_for_messages(self, tokenizer, expected):
        assert (
            tokenizer.count_tokens(
                [{"role": "system", "content": "foobar baz"}, {"role": "user", "content": "how foobar am I?"}]
            )
            == expected
        )

    @pytest.mark.parametrize(("tokenizer", "expected"), [("not-real-model", 19)], indirect=["tokenizer"])
    def test_token_count_for_messages_unknown_model(self, tokenizer, expected):
        with pytest.raises(NotImplementedError):
            tokenizer.count_tokens(
                [{"role": "system", "content": "foobar baz"}, {"role": "user", "content": "how foobar am I?"}]
            )

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("gpt-4-1106", 127987),
            ("gpt-4o", 127987),
            ("gpt-4-32k", 32755),
            ("gpt-4", 8179),
            ("gpt-3.5-turbo-16k", 16371),
            ("gpt-3.5-turbo", 4083),
            ("gpt-35-turbo-16k", 16371),
            ("gpt-35-turbo", 4083),
            ("text-embedding-ada-002", 8186),
            ("text-embedding-ada-001", 2041),
            ("text-embedding-3-small", 8186),
            ("text-embedding-3-large", 8186),
        ],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [
            ("gpt-4-1106", 4091),
            ("gpt-4-32k", 4091),
            ("gpt-4", 4091),
            ("gpt-4o", 4091),
            ("gpt-3.5-turbo-16k", 4091),
            ("gpt-3.5-turbo", 4091),
            ("gpt-35-turbo-16k", 4091),
            ("gpt-35-turbo", 4091),
            ("text-embedding-ada-002", 4091),
            ("text-embedding-ada-001", 4091),
            ("text-embedding-3-small", 4091),
            ("text-embedding-3-large", 4091),
        ],
        indirect=["tokenizer"],
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
