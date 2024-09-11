import json

import pytest

from griptape.loaders.csv_loader import CsvLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestCsvLoader:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def loader(self, request):
        encoding = request.param
        if encoding is None:
            return CsvLoader(embedding_driver=MockEmbeddingDriver())
        else:
            return CsvLoader(embedding_driver=MockEmbeddingDriver(), encoding=encoding)

    @pytest.fixture()
    def loader_with_pipe_delimiter(self):
        return CsvLoader(embedding_driver=MockEmbeddingDriver(), delimiter="|")

    @pytest.fixture(params=["bytes_from_resource_path", "str_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("test-1.csv")

        artifacts = loader.load(source)

        assert len(artifacts) == 10
        first_artifact = artifacts[0]
        assert first_artifact.value == "Foo: foo1\nBar: bar1"
        assert first_artifact.embedding == [0, 1]

    def test_load_delimiter(self, loader_with_pipe_delimiter, create_source):
        source = create_source("test-pipe.csv")

        artifacts = loader_with_pipe_delimiter.load(source)

        assert len(artifacts) == 10
        first_artifact = artifacts[0]
        assert first_artifact.value == "Bar: foo1\nFoo: bar1"
        assert first_artifact.embedding == [0, 1]

    def test_load_collection(self, loader, create_source):
        resource_paths = ["test-1.csv", "test-2.csv"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}
        assert collection.keys() == keys

        assert collection[loader.to_key(sources[0])][0].value == "Foo: foo1\nBar: bar1"
        assert collection[loader.to_key(sources[0])][0].embedding == [0, 1]

        assert collection[loader.to_key(sources[1])][0].value == "Bar: bar1\nFoo: foo1"
        assert collection[loader.to_key(sources[1])][0].embedding == [0, 1]

    def test_formatter_fn(self, loader, create_source):
        loader.formatter_fn = lambda value: json.dumps(value)
        source = create_source("test-1.csv")

        artifacts = loader.load(source)

        assert len(artifacts) == 10
        assert artifacts[0].value == '{"Foo": "foo1", "Bar": "bar1"}'
