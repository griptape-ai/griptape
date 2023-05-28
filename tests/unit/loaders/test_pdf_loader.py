import os
import pytest
from griptape.loaders import PdfLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestPdfLoader:
    @pytest.fixture
    def loader(self):
        return PdfLoader(
            embedding_driver=MockEmbeddingDriver(),
            max_tokens=MAX_TOKENS
        )

    def test_load(self, loader):
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/bitcoin.pdf"
        )

        list_artifact = loader.load(path)

        assert len(list_artifact.value) == 135
        assert list_artifact.value[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert list_artifact.value[0].embedding == [0, 1]
