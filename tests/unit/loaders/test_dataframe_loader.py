import os

import pandas as pd
import pytest

from griptape.loaders.dataframe_loader import DataFrameLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestDataFrameLoader:
    @pytest.fixture()
    def loader(self):
        return DataFrameLoader(embedding_driver=MockEmbeddingDriver())

    def test_load_with_path(self, loader):
        # test loading a file delimited by comma
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/test-1.csv")

        artifacts = loader.load(pd.read_csv(path))

        assert len(artifacts) == 10
        first_artifact = artifacts[0].value
        assert first_artifact["Foo"] == "foo1"
        assert first_artifact["Bar"] == "bar1"

        assert artifacts[0].embedding == [0, 1]

    def test_load_collection_with_path(self, loader):
        path1 = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/test-1.csv")
        path2 = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/test-2.csv")
        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)
        collection = loader.load_collection([df1, df2])

        key1 = loader.to_key(df1)
        key2 = loader.to_key(df2)

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
