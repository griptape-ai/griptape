import cohere
import pytest
from griptape.tokenizers import CohereTokenizer


class TestCohereTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return CohereTokenizer(client=cohere.Client("foobar"))

    def test_init(self, tokenizer):
        assert tokenizer
