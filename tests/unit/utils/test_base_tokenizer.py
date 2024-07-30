import logging

from tests.mocks.mock_tokenizer import MockTokenizer


class TestBaseTokenizer:
    def test_default_tokens(self, caplog):
        with caplog.at_level(logging.WARNING):
            tokenizer = MockTokenizer(model="gpt2")

            assert tokenizer.max_input_tokens == 4096
            assert tokenizer.max_output_tokens == 1000

            assert "gpt2 not found" in caplog.text
