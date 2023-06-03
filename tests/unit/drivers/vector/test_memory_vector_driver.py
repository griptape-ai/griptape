import pytest

from griptape import utils
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
        driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == utils.str_to_hash(str([0, 1]))

        driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 1

    def test_query(self, driver):
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
