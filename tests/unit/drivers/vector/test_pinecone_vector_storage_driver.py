import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import PineconeVectorStoreDriver
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

        assert driver.upsert_text_artifact(artifact) == driver._get_default_vector_id("foo")

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0, 1, 2], vector_id="foo") == "foo"
        assert isinstance(driver.upsert_vector([0, 1, 2]), str)

    def test_upsert_text(self, driver):
        assert driver.upsert_text("foo", vector_id="foo") == "foo"
        assert isinstance(driver.upsert_text("foo"), str)

    def test_query(self, driver):
        results = driver.query("test")

        assert results[0].vector == [0, 1, 0]
        assert results[0].id == "foo"
