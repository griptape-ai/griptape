import pytest
from griptape.drivers import MemoryVectorStorageDriver
from griptape.engines import QueryEngine
from griptape.loaders import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestQueryEngine:
    @pytest.fixture
    def engine(self):
        return QueryEngine(
            vector_storage_driver=MemoryVectorStorageDriver(
                embedding_driver=MockEmbeddingDriver(),
            ),
            prompt_driver=MockPromptDriver()
        )

    def test_insert_and_query(self, engine):
        artifacts = TextLoader(max_tokens=MAX_TOKENS).load(
            gen_paragraph(MAX_TOKENS, engine.prompt_driver.tokenizer, ". ")
        )

        engine.insert(artifacts)

        assert engine.query("foo").value.startswith("mock output")
