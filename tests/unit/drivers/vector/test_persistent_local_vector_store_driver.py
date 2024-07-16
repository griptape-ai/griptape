import os
import tempfile

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.drivers.vector.test_base_local_vector_store_driver import BaseLocalVectorStoreDriver


class TestPersistentLocalVectorStoreDriver(BaseLocalVectorStoreDriver):
    @pytest.fixture()
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture()
    def driver(self, temp_dir):
        persist_file = os.path.join(temp_dir, "store.json")

        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver(), persist_file=persist_file)

    def test_persistence(self, driver, temp_dir):
        persist_file = os.path.join(temp_dir, "store.json")

        driver.upsert_text_artifact(TextArtifact("persistent foobar"))

        new_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver(), persist_file=persist_file)

        assert new_driver.query("persistent foobar")[0].to_artifact().value == "persistent foobar"
