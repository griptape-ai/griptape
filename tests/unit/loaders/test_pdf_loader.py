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

        artifacts = loader.load(path)

        assert len(artifacts) == 149
        assert artifacts[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader):
        path1 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/bitcoin.pdf"
        )
        path2 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/bitcoin-2.pdf"
        )

        artifacts = loader.load_collection([path1, path2])

        assert list(artifacts.keys()) == [path1, path2]
        assert len(artifacts[path1]) == 149
        assert artifacts[path1][0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[path1][0].embedding == [0, 1]
        assert len(artifacts[path2]) == 149
        assert artifacts[path2][0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[path2][0].embedding == [0, 1]
