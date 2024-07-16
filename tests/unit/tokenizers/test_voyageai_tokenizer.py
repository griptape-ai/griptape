import pytest

from griptape.tokenizers import VoyageAiTokenizer


class TestVoyageAiTokenizer:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("voyageai.Client")
        mock_client.return_value.count_tokens.return_value = 5

        return mock_client

    @pytest.fixture()
    def tokenizer(self, request):
        return VoyageAiTokenizer(model=request.param)

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [("voyage-large-2", 5), ("voyage-code-2", 5), ("voyage-2", 5), ("voyage-lite-02-instruct", 5)],
        indirect=["tokenizer"],
    )
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [("voyage-large-2", 15995), ("voyage-code-2", 15995), ("voyage-2", 3995), ("voyage-lite-02-instruct", 3995)],
        indirect=["tokenizer"],
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"),
        [("voyage-large-2", 0), ("voyage-code-2", 0), ("voyage-2", 0), ("voyage-lite-02-instruct", 0)],
        indirect=["tokenizer"],
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
