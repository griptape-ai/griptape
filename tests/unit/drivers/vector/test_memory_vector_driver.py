import pytest
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import MemoryVectorDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestMemoryVectorDriver:
    @pytest.fixture
    def driver(self):
        return MemoryVectorDriver(
            embedding_driver=MockEmbeddingDriver(),
        )

    def test_insert(self, driver):
        artifact_id = driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == artifact_id

        driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 2

    def test_query(self, driver):
        driver.upsert_text_artifact(
            TextArtifact("foobar"),
            namespace="test-namespace"
        )

        assert len(driver.query("foobar")) == 1
        assert len(driver.query("foobar", namespace="bad-namespace")) == 0
        assert len(driver.query("foobar", namespace="test-namespace")) == 1
        assert driver.query("foobar")[0].vector == [0, 1]
        assert BaseArtifact.from_json(driver.query("foobar")[0].meta["artifact"]).value == "foobar"

    def test_load_vector(self, driver):
        vector_id = driver.upsert_text_artifact(
            TextArtifact("foobar"),
            namespace="test-namespace"
        )

        assert driver.load_vector(vector_id, namespace="test-namespace").id == vector_id

    def test_load_vectors(self, driver):
        driver.upsert_text_artifact(TextArtifact("foobar 1"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 2"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 3"), namespace="test-namespace-2")

        assert len(driver.load_vectors()) == 3
        assert len(driver.load_vectors("test-namespace-1")) == 2
        assert len(driver.load_vectors("test-namespace-2")) == 1
