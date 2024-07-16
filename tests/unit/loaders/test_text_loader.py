import pytest

from griptape.loaders.text_loader import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestTextLoader:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def loader(self, request):
        encoding = request.param
        if encoding is None:
            return TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())
        else:
            return TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver(), encoding=encoding)

    @pytest.fixture(params=["bytes_from_resource_path", "str_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("test.txt")

        artifacts = loader.load(source)

        assert len(artifacts) == 39
        assert artifacts[0].value.startswith("foobar foobar foobar")
        assert artifacts[0].encoding == loader.encoding
        assert artifacts[0].embedding == [0, 1]

    def test_load_collection(self, loader, create_source):
        resource_paths = ["test.txt"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}
        assert collection.keys() == keys

        key = next(iter(keys))
        artifacts = collection[key]
        assert len(artifacts) == 39

        artifact = artifacts[0]
        assert artifact.embedding == [0, 1]
        assert artifact.encoding == loader.encoding
