import pytest
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestLocalVectorStoreDriver:
    @pytest.fixture
    def driver(self):
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

    def test_upsert(self, driver):
        namespace = driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == namespace

        driver.upsert_text_artifact(TextArtifact("foobar"))

        assert len(driver.entries) == 2

    def test_upsert_multiple(self, driver):
        driver.upsert_text_artifacts(
            {"foo": [TextArtifact("foo")], "bar": [TextArtifact("bar")]}
        )

        foo_entries = driver.load_entries("foo")
        bar_entries = driver.load_entries("bar")

        assert len(driver.entries) == 2
        assert (
            BaseArtifact.from_json(foo_entries[0].meta["artifact"]).value
            == "foo"
        )
        assert (
            BaseArtifact.from_json(bar_entries[0].meta["artifact"]).value
            == "bar"
        )

    def test_query(self, driver):
        vector_id = driver.upsert_text_artifact(
            TextArtifact("foobar"), namespace="test-namespace"
        )

        assert len(driver.query("foobar")) == 1
        assert len(driver.query("foobar", namespace="bad-namespace")) == 0
        assert len(driver.query("foobar", namespace="test-namespace")) == 1
        assert driver.query("foobar")[0].vector == []
        assert driver.query("foobar", include_vectors=True)[0].vector == [0, 1]
        assert (
            BaseArtifact.from_json(
                driver.query("foobar")[0].meta["artifact"]
            ).value
            == "foobar"
        )
        assert driver.query("foobar")[0].id == vector_id

    def test_load_entry(self, driver):
        vector_id = driver.upsert_text_artifact(
            TextArtifact("foobar"), namespace="test-namespace"
        )

        assert (
            driver.load_entry(vector_id, namespace="test-namespace").id
            == vector_id
        )

    def test_load_entries(self, driver):
        driver.upsert_text_artifact(
            TextArtifact("foobar 1"), namespace="test-namespace-1"
        )
        driver.upsert_text_artifact(
            TextArtifact("foobar 2"), namespace="test-namespace-1"
        )
        driver.upsert_text_artifact(
            TextArtifact("foobar 3"), namespace="test-namespace-2"
        )

        assert len(driver.load_entries()) == 3
        assert len(driver.load_entries("test-namespace-1")) == 2
        assert len(driver.load_entries("test-namespace-2")) == 1
