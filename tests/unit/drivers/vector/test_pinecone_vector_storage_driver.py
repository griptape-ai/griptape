from unittest.mock import call

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers.vector import BaseVectorStoreDriver
from griptape.drivers.vector.pinecone import PineconeVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestPineconeVectorStorageDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        # Create a fake response
        fake_query_response = {
            "matches": [{"id": "foo", "values": [0, 1, 0], "score": 42, "metadata": {"foo": "bar"}}],
            "namespace": "foobar",
        }

        mock_client = mocker.patch("pinecone.Pinecone")
        mock_index = mock_client().Index()
        mock_index.upsert.return_value = None
        mock_index.query.return_value = fake_query_response
        mock_index.create_index.return_value = None

        # Return the mock index when the Pinecone client is called
        mock_client.Index.return_value = mock_index

        return mock_client

    @pytest.fixture()
    def driver(self, mock_client):
        return PineconeVectorStoreDriver(
            api_key="foobar",
            index_name="test",
            environment="test",
            embedding_driver=MockEmbeddingDriver(),
            client=mock_client,
        )

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")

        assert driver.upsert(artifact) == driver._get_default_vector_id("foo")

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0, 1, 2], vector_id="foo") == "foo"
        assert isinstance(driver.upsert_vector([0, 1, 2]), str)

    def test_upsert_text(self, driver):
        assert driver.upsert("foo", vector_id="foo") == "foo"
        assert isinstance(driver.upsert("foo"), str)

    def test_upsert_vectors(self, driver):
        entries = [
            BaseVectorStoreDriver.Entry(id="foo", vector=[0, 1], meta={"foo": "bar"}, namespace="ns1"),
            BaseVectorStoreDriver.Entry(id="bar", vector=[1, 0], namespace="ns2"),
            BaseVectorStoreDriver.Entry(id="baz", vector=[1, 1], namespace="ns1"),
        ]

        assert driver.upsert_vectors(entries) == ["foo", "bar", "baz"]
        assert driver.index.upsert.call_args_list == [
            call(
                vectors=[("foo", [0, 1], {"foo": "bar"}), ("baz", [1, 1], None)],
                namespace="ns1",
                batch_size=100,
                show_progress=False,
            ),
            call(vectors=[("bar", [1, 0], None)], namespace="ns2", batch_size=100, show_progress=False),
        ]

    def test_upsert_vectors_empty(self, driver):
        assert driver.upsert_vectors([]) == []
        driver.index.upsert.assert_not_called()

    def test_upsert_vectors_duplicate_ids(self, driver):
        entries = [
            BaseVectorStoreDriver.Entry(id="foo", vector=[0, 1]),
            BaseVectorStoreDriver.Entry(id="foo", vector=[1, 0]),
        ]

        assert driver.upsert_vectors(entries) == ["foo", "foo"]
        assert driver.index.upsert.call_args.kwargs["vectors"] == [("foo", [1, 0], None)]

    def test_upsert_vectors_batch_size(self, driver):
        driver.batch_size = 10
        entries = [BaseVectorStoreDriver.Entry(id="foo", vector=[0, 1])]

        driver.upsert_vectors(entries)
        assert driver.index.upsert.call_args.kwargs["batch_size"] == 10

        driver.upsert_vectors(entries, batch_size=5, show_progress=True)
        assert driver.index.upsert.call_args.kwargs["batch_size"] == 5
        assert driver.index.upsert.call_args.kwargs["show_progress"] is True

    def test_upsert_collection(self, driver):
        ids = driver.upsert_collection({"foo": [TextArtifact("a"), TextArtifact("b"), TextArtifact("c")]})

        assert ids == {"foo": [driver._get_default_vector_id(value) for value in ["a", "b", "c"]]}
        driver.index.upsert.assert_called_once()
        assert [vector[0] for vector in driver.index.upsert.call_args.kwargs["vectors"]] == ids["foo"]

    def test_query_vector(self, driver):
        results = driver.query_vector([0.0, 0.5])

        assert results[0].vector == [0, 1, 0]
        assert results[0].id == "foo"

    def test_query(self, driver):
        results = driver.query("test")

        assert results[0].vector == [0, 1, 0]
        assert results[0].id == "foo"
