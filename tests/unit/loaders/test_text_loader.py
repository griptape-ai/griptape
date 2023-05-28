import pytest

from griptape.artifacts import TextArtifact
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
        list_artifact = loader.load(text)

        assert len(list_artifact.value) == 3
        assert list_artifact.value[0].value.startswith("foo-0 foo-1")
        assert list_artifact.value[0].embedding == [0, 1]

    def test_load_short(self, loader):
        text = gen_paragraph(MAX_TOKENS, loader.tokenizer, " ")
        text_artifact = loader.load(text)

        assert isinstance(text_artifact, TextArtifact)
        assert text_artifact.value.startswith("foo-0 foo-1")
        assert text_artifact.embedding == [0, 1]