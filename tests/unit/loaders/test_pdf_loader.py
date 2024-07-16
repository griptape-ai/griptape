import pytest

from griptape.loaders import PdfLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestPdfLoader:
    @pytest.fixture()
    def loader(self):
        return PdfLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())

    @pytest.fixture()
    def create_source(self, bytes_from_resource_path):
        return bytes_from_resource_path

    def test_load(self, loader, create_source):
        source = create_source("bitcoin.pdf")

        artifacts = loader.load(source)

        assert len(artifacts) == 151
        assert artifacts[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[-1].value.endswith('its applications," 1957.\n9')
        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader, create_source):
        resource_paths = ["bitcoin.pdf", "bitcoin-2.pdf"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}

        assert collection.keys() == keys

        for key in keys:
            artifact = collection[key]
            assert len(artifact) == 151
            assert artifact[0].value.startswith("Bitcoin: A Peer-to-Peer")
            assert artifact[-1].value.endswith('its applications," 1957.\n9')
            assert artifact[0].embedding == [0, 1]
