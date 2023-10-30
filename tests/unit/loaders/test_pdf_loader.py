import os
import pytest
from griptape import utils
from griptape.loaders import PdfLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestPdfLoader:
    @pytest.fixture
    def loader(self):
        return PdfLoader(
            max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver()
        )

    def test_load(self, loader):
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/bitcoin.pdf",
        )

        artifacts = loader.load(path)

        assert len(artifacts) == 149
        assert artifacts[0].value.startswith("Bitcoin: A Peer-to-Peer")

        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader):
        path1 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/bitcoin.pdf",
        )
        path2 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/bitcoin-2.pdf",
        )
        key1 = utils.str_to_hash(path1)
        key2 = utils.str_to_hash(path2)

        artifacts = loader.load_collection([path1, path2])

        assert list(artifacts.keys()) == [key1, key2]
        assert len(artifacts[key1]) == 149
        assert artifacts[key1][0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert len(artifacts[key2]) == 149
        assert artifacts[key2][0].value.startswith("Bitcoin: A Peer-to-Peer")

        assert artifacts[key1][0].embedding == [0, 1]
