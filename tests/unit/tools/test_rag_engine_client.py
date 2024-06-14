from griptape.drivers import LocalVectorStoreDriver
from griptape.tools import RagEngineClient
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils.defaults import rag_engine


class TestRagEngineClient:
    def test_search(self):
        vector_store_driver = LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
        tool = RagEngineClient(description="Test", rag_engine=rag_engine(MockPromptDriver(), vector_store_driver))

        assert tool.search({"values": {"query": "test"}}).value == "mock output"
