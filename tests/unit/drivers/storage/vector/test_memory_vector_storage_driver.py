import pytest
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import MemoryVectorStorageDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestMemoryVectorStorageDriver:
    @pytest.fixture
    def driver(self):
        return MemoryVectorStorageDriver(
            embedding_driver=MockEmbeddingDriver(),
        )

    def test_insert_and_query(self, driver):
        driver.upsert_text_artifact(
            TextArtifact("foobar"),
            vector_id="test-id",
            namespace="test-namespace"
        )

        assert len(driver.query("foobar")) == 1
        assert len(driver.query("foobar", namespace="bad-namespace")) == 0
        assert len(driver.query("foobar", namespace="test-namespace")) == 1
        assert driver.query("foobar")[0].vector == [0, 1]
        assert BaseArtifact.from_json(driver.query("foobar")[0].meta["artifact"]).value == "foobar"
