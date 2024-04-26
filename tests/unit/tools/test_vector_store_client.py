import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.tools import VectorStoreClient
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestVectorStoreClient:
    @pytest.fixture(autouse=True)
    def mock_try_runt(self, mocker):
        mocker.patch("griptape.drivers.OpenAiChatPromptDriver.try_run", return_value=TextArtifact("foobar"))

        mocker.patch("griptape.drivers.OpenAiEmbeddingDriver.try_embed_chunk", return_value=[0, 1])

    def test_search(self):
        tool = VectorStoreClient(
            description="Test",
            query_engine=VectorQueryEngine(
                prompt_driver=MockPromptDriver(mock_output="foobar"),
                vector_store_driver=LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver()),
            ),
            off_prompt=False,
        )

        assert tool.search({"values": {"query": "test"}}).value == "foobar"
