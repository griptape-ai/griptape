import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers.vector.local import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.drivers.vector.test_base_vector_store_driver import TestBaseVectorStoreDriver


class TestLocalVectorStoreDriver(TestBaseVectorStoreDriver):
    @pytest.fixture()
    def driver(self):
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

    def test_upsert_collection_dict(self, driver):
        driver.upsert_collection({"foo": [TextArtifact("bar"), TextArtifact("baz")], "bar": [TextArtifact("bar")]})

        assert len(driver.load_artifacts(namespace="foo")) == 2
        assert len(driver.load_artifacts(namespace="bar")) == 1

    def test_upsert_collection_list(self, driver):
        driver.upsert_collection([TextArtifact("bar"), TextArtifact("baz")])

        assert len(driver.load_artifacts(namespace="foo")) == 0
        assert len(driver.load_artifacts()) == 2

    def test_upsert_collection_stress_test(self, driver):
        driver.upsert_collection(
            {
                "test1": [TextArtifact(f"foo-{i}") for i in range(1000)],
                "test2": [TextArtifact(f"foo-{i}") for i in range(1000)],
                "test3": [TextArtifact(f"foo-{i}") for i in range(1000)],
            }
        )

        assert len(driver.query("foo", namespace="test1")) == 1000
        assert len(driver.query("foo", namespace="test2")) == 1000
        assert len(driver.query("foo", namespace="test3")) == 1000

    def test_query_vector(self, driver):
        driver.upsert_collection({"foo": [TextArtifact("foo bar")]})

        result = driver.query_vector([1.0, 1.0], count=1, include_vectors=True)

        assert len(result) == 1
        assert result[0].to_artifact().value == "foo bar"
        assert result[0].id is not None
        assert result[0].vector == [0, 1]
        assert result[0].score is not None
        assert result[0].namespace == "foo"

    @pytest.mark.parametrize("execution_number", range(1000))
    def test_upsert_collection_meta(self, driver, mocker, execution_number):
        spy = mocker.spy(driver, "upsert_vector")
        artifact_1 = TextArtifact("foo bar", id="foo")
        artifact_2 = TextArtifact("bar foo", id="bar")

        driver.upsert_collection({"foo": [artifact_1, artifact_2]}, meta={"foo": "bar"})

        assert spy.call_args_list[0].kwargs["meta"]["artifact"] != spy.call_args_list[1].kwargs["meta"]["artifact"]
