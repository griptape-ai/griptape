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
        key1 = "aae8c834b1d45eac18df3717f9bb7938476da550056b8b17febc9e490115db6b"
        key2 = "644e9ef478e7abcfa83b6016f2444e1cde42e6bbc194fd4329143993a04dcf40"

        artifacts = loader.load_collection([path1, path2])

        assert list(artifacts.keys()) == [key1, key2]
        assert len(artifacts[key1]) == 149
        assert artifacts[key1][0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[key1][0].embedding == [0, 1]
        assert len(artifacts[key2]) == 149
        assert artifacts[key2][0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[key2][0].embedding == [0, 1]
