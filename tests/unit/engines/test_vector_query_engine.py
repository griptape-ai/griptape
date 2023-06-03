import pytest
from griptape.drivers import MemoryVectorDriver
from griptape.engines import VectorQueryEngine
from griptape.loaders import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestVectorQueryEngine:
    @pytest.fixture
    def engine(self):
        return VectorQueryEngine(
            vector_driver=MemoryVectorDriver(
                embedding_driver=MockEmbeddingDriver(),
            ),
            prompt_driver=MockPromptDriver()
        )

    def test_upsert_and_query(self, engine):
        artifacts = TextLoader(max_tokens=MAX_TOKENS).load(
            gen_paragraph(MAX_TOKENS, engine.prompt_driver.tokenizer, ". ")
        )

        engine.insert(artifacts)

        assert engine.query("foo").value.startswith("mock output")
