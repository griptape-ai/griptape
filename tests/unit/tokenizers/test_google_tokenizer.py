from unittest.mock import Mock

import pytest

from griptape.common import PromptStack
from griptape.common.prompt_stack.messages.message import Message
from griptape.tokenizers import GoogleTokenizer


class TestGoogleTokenizer:
    @pytest.fixture(autouse=True)
    def mock_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mock_generative_model.return_value.count_tokens.return_value = Mock(total_tokens=5)

        return mock_generative_model

    @pytest.fixture()
    def tokenizer(self, request):
        return GoogleTokenizer(model=request.param, api_key="1234")

    @pytest.mark.parametrize(("tokenizer", "expected"), [("gemini-2.0-flash", 5)], indirect=["tokenizer"])
    def test_token_count(self, tokenizer, expected):
        assert tokenizer.count_tokens("foo bar huzzah") == expected
        assert tokenizer.count_tokens(PromptStack(messages=[Message(content="foo", role="user")])) == expected
        assert tokenizer.count_tokens(["foo", "bar", "huzzah"]) == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"), [("gemini-1.5-pro", 2097147), ("gemini-2.0-flash", 1048571)], indirect=["tokenizer"]
    )
    def test_input_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == expected
        assert tokenizer.count_input_tokens_left(["foo", "bar", "huzzah"]) == expected

    @pytest.mark.parametrize(
        ("tokenizer", "expected"), [("gemini-1.5-pro", 8187), ("gemini-2.0-flash", 8187)], indirect=["tokenizer"]
    )
    def test_output_tokens_left(self, tokenizer, expected):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == expected
        assert tokenizer.count_output_tokens_left(["foo", "bar", "huzzah"]) == expected
