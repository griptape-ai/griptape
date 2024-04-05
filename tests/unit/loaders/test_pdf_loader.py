import os
from pathlib import Path
from typing import IO
import pytest
from griptape import utils
from griptape.loaders import PdfLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestPdfLoader:
    @pytest.fixture
    def loader(self):
        return PdfLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())

    @pytest.fixture(params=["bytes_from_resource_path", "path_from_resource_path", "binary_io_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("bitcoin.pdf")

        artifacts = loader.load(source)

        assert len(artifacts) == 151
        assert artifacts[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifacts[-1].value.endswith('its applications," 1957.\n9')
        assert artifacts[0].embedding == [0, 1]

    def test_load_raises_on_text_io_source(self, text_io_from_resource_path, loader):
        source = text_io_from_resource_path("bitcoin.pdf")

        with pytest.raises(ValueError) as e:
            loader.load(source)

        assert "Unsupported source type" in str(e.value)

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
