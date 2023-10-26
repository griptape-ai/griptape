import os
import pytest
from griptape import utils
from griptape.loaders.csv_loader import CsvLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestCsvLoader:
    @pytest.fixture
    def loaders(self):
        return (
            CsvLoader(embedding_driver=MockEmbeddingDriver()),
            CsvLoader(embedding_driver=MockEmbeddingDriver(), delimiter="|"),
        )

    def test_load_with_path(self, loaders):
        (loader, loader_pipe) = loaders
        # test loading a file delimited by comma
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test-1.csv",
        )

        artifacts = loader.load(path)

        assert len(artifacts) == 10
        first_artifact = artifacts[0].value
        assert first_artifact["Foo"] == "foo1"
        assert first_artifact["Bar"] == "bar1"

        # test loading a file delimited by pipe
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test-pipe.csv",
        )

        artifacts = loader_pipe.load(path)

        assert len(artifacts) == 10
        first_artifact = artifacts[0].value
        assert first_artifact["Bar"] == "foo1"
        assert first_artifact["Foo"] == "bar1"

        assert artifacts[0].embedding == [0, 1]

    def test_load_collection_with_path(self, loaders):
        loader = loaders[0]

        path1 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test-1.csv",
        )
        path2 = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test-2.csv",
        )
        collection = loader.load_collection([path1, path2])

        key1 = utils.str_to_hash(str(path1))
        key2 = utils.str_to_hash(str(path2))

        assert list(collection.keys()) == [key1, key2]

        artifacts = collection[key1]
        assert len(artifacts) == 10
        first_artifact = artifacts[0].value
        assert first_artifact["Foo"] == "foo1"
        assert first_artifact["Bar"] == "bar1"

        artifacts = collection[key2]
        assert len(artifacts) == 10
        first_artifact = artifacts[0].value
        assert first_artifact["Bar"] == "bar1"
        assert first_artifact["Foo"] == "foo1"

        assert artifacts[0].embedding == [0, 1]
