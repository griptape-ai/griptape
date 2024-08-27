import pytest

from griptape.drivers import LocalVectorStoreDriver
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import TextLoaderRetrievalRagModule
from griptape.loaders import WebLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestTextLoaderRetrievalRagModule:
    @pytest.fixture(autouse=True)
    def _mock_trafilatura_fetch_url(self, mocker):
        mocker.patch("trafilatura.fetch_url", return_value="<html>foobar</html>")

    def test_run(self):
        embedding_driver = MockEmbeddingDriver()

        module = TextLoaderRetrievalRagModule(
            loader=WebLoader(),
            vector_store_driver=LocalVectorStoreDriver(embedding_driver=embedding_driver),
            source="https://www.griptape.ai",
        )

        assert module.run(RagContext(query="foo"))[0].value == "foobar"
