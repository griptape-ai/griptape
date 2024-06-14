import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.tools import VectorStoreClient
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestVectorStoreClient:
    @pytest.fixture(autouse=True)
    def mock_try_run(self, mocker):
        mocker.patch("griptape.drivers.OpenAiEmbeddingDriver.try_embed_chunk", return_value=[0, 1])

    def test_search(self):
        driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool = VectorStoreClient(description="Test", vector_store_driver=driver)

        driver.upsert_text_artifacts({"test": [TextArtifact("foo"), TextArtifact("bar")]})

        assert [a.value for a in tool.search({"values": {"query": "test"}})] == ["foo", "bar"]
