import pytest
from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_tool.tool import MockTool


class TestTextToolMemory:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.summarizers.PromptDriverSummarizer.summarize_text",
            return_value="foobar summary"
        )

        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

    @pytest.fixture
    def memory(self):
        query_engine = VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        )

        return TextToolMemory(
            id="MyMemory",
            query_engine=query_engine
        )

    def test_init(self, memory):
        assert memory.id == "MyMemory"

    def test_process_output(self, memory):
        assert memory.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )

    def test_process_output_with_many_artifacts(self, memory):
        assert memory.process_output(MockTool().test, [TextArtifact("foo")]).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )

    def test_summarize(self, memory):
        memory.query_engine.vector_store_driver.upsert_text_artifact(
            TextArtifact("foobar"), namespace="foobar"
        )

        assert memory.summarize(
            {"values": {"artifact_namespace": "foobar"}}
        ).value == "foobar summary"

    def test_query(self, memory):
        assert memory.search(
            {"values": {"query": "foobar", "artifact_namespace": "foo"}}
        ).value == "foobar"

    def test_load_namespace_artifacts(self, memory):
        memory.query_engine.vector_store_driver.upsert_text_artifacts(
            {"test": [TextArtifact("foo"), TextArtifact("bar")]}
        )

        assert len(memory.load_namespace_artifacts("test")) == 2
