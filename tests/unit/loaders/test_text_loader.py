import pytest
from griptape.loaders.text_loader import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestTextLoader:
    @pytest.fixture
    def loader(self):
        return TextLoader(
            embedding_driver=MockEmbeddingDriver(),
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        text = gen_paragraph(MAX_TOKENS * 2, loader.tokenizer, " ")
        artifacts = loader.load(text)

        assert len(artifacts) == 3
        assert artifacts[0].value.startswith("foo-0 foo-1")
        assert artifacts[0].embedding == [0, 1]
