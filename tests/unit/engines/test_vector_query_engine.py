import pytest
from griptape.artifacts import TextArtifact, BaseArtifact
from griptape.drivers import LocalVectorStoreDriver
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
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver(),
            ),
            prompt_driver=MockPromptDriver()
        )

    def test_query(self, engine):
        artifacts = TextLoader(max_tokens=MAX_TOKENS).load(
            gen_paragraph(MAX_TOKENS, engine.prompt_driver.tokenizer, ". ")
        )

        [engine.upsert_text_artifact(a) for a in artifacts]

        assert engine.query("foo").value.startswith("mock output")

    def test_upsert_text_artifact(self, engine):
        engine.upsert_text_artifact(
            TextArtifact("foobar"),
            namespace="test"
        )

        assert BaseArtifact.from_json(engine.vector_store_driver.load_entries()[0].meta["artifact"]).value == "foobar"

