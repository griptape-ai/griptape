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
            vector_store_driver=LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver()),
            prompt_driver=MockPromptDriver(),
        )

    def test_query(self, engine):
        artifacts = TextLoader(max_tokens=MAX_TOKENS).load(
            gen_paragraph(MAX_TOKENS, engine.prompt_driver.tokenizer, ". ")
        )

        [engine.upsert_text_artifact(a) for a in artifacts]

        assert engine.query("foo").value.startswith("mock output")

    def test_upsert_text_artifact(self, engine):
        engine.upsert_text_artifact(TextArtifact("foobar"), namespace="test")

        assert BaseArtifact.from_json(engine.vector_store_driver.load_entries()[0].meta["artifact"]).value == "foobar"

    def test_prompt_creation(self, engine):
        system_message = engine.system_template_generator.render(rulesets=["*RULESET*"])
        user_message = engine.user_template_generator.render(
            metadata="*META*", query="*QUESTION*", text_segments=["*TEXT SEGMENT 1*", "*TEXT SEGMENT 2*"]
        )

        assert "*RULESET*" in system_message

        assert "*META*" in user_message
        assert "*QUESTION*" in user_message
        assert "*TEXT SEGMENT 1*" in user_message
        assert "*TEXT SEGMENT 2*" in user_message

    def test_upsert_text_artifacts(self, engine):
        engine.upsert_text_artifacts(artifacts=[TextArtifact("foobar1"), TextArtifact("foobar2")], namespace="test")

        assert BaseArtifact.from_json(engine.vector_store_driver.load_entries()[0].meta["artifact"]).value == "foobar1"
        assert BaseArtifact.from_json(engine.vector_store_driver.load_entries()[1].meta["artifact"]).value == "foobar2"

    def test_load_artifacts(self, engine):
        engine.upsert_text_artifacts(artifacts=[TextArtifact("foobar1"), TextArtifact("foobar2")], namespace="test")

        assert len(engine.load_artifacts("doesntexist")) == 0
        assert len(engine.load_artifacts("test")) == 2
