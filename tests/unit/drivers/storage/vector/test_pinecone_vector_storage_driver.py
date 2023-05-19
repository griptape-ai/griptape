import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import PineconeVectorStorageDriver


class TestOpenAiEmbeddingDriver:
    """
    Don't move the driver into a fixture. There is something wrong with how it gets
    instantiated, which results in GitHub test actions to hang forever.
    """

    @pytest.fixture(autouse=True)
    def mock_openai_embedding_create(self, mocker):
        # Create a fake response
        fake_query_response = {
            "matches": [
                {
                    "values": [0, 1, 0],
                    "score": 42,
                    "metadata": {
                        "foo": "bar"
                    }
                }
            ],
            "namespace": "foobar"
        }

        mocker.patch('pinecone.init', return_value=None)
        mocker.patch('pinecone.Index.upsert', return_value=None)
        mocker.patch('pinecone.Index.query', return_value=fake_query_response)
        mocker.patch('pinecone.create_index', return_value=None)

    def test_insert_test_artifact(self):
        driver = PineconeVectorStorageDriver(
            api_key="foobar",
            index_name="test"
        )
        
        assert driver.insert_text_artifact(
            TextArtifact("foo"),
            vector_id="foo"
        ) == "foo"

    def test_insert_vector(self):
        driver = PineconeVectorStorageDriver(
            api_key="foobar",
            index_name="test"
        )

        assert driver.insert_vector([0, 1, 2], vector_id="foo") == "foo"
        assert isinstance(driver.insert_vector([0, 1, 2]), str)

    def test_insert_text(self):
        driver = PineconeVectorStorageDriver(
            api_key="foobar",
            index_name="test"
        )

        assert driver.insert_text("foo", vector_id="foo") == "foo"
        assert isinstance(driver.insert_text("foo"), str)

    def test_query(self):
        driver = PineconeVectorStorageDriver(
            api_key="foobar",
            index_name="test"
        )

        assert driver.query("test")[0].vector == [0, 1, 0]

    def test_create_index(self):
        driver = PineconeVectorStorageDriver(
            api_key="foobar",
            index_name="test"
        )

        assert driver.create_index("test") is None
