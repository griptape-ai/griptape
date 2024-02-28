import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import PineconeVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestPineconeVectorStorageDriver:
    """
    This should really be under `unit` but the Pinecone client results
    in tests hanging on GitHub.
    """

    @pytest.fixture(autouse=True)
    def mock_pinecone(self, mocker):
        # Create a fake response
        fake_query_response = {
            "matches": [{"id": "foo", "values": [0, 1, 0], "score": 42, "metadata": {"foo": "bar"}}],
            "namespace": "foobar",
        }

        mocker.patch("pinecone.init", return_value=None)
        mocker.patch("pinecone.Index.upsert", return_value=None)
        mocker.patch("pinecone.Index.query", return_value=fake_query_response)
        mocker.patch("pinecone.create_index", return_value=None)

    @pytest.fixture
    def driver(self):
        return PineconeVectorStoreDriver(
            api_key="foobar", index_name="test", environment="test", embedding_driver=MockEmbeddingDriver()
        )

    def test_upsert_text_artifact(self, driver):
        artifact = TextArtifact("foo")

        assert driver.upsert_text_artifact(artifact) == artifact.id

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
