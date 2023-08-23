import pytest
from griptape.artifacts import TextArtifact, CsvRowArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from griptape.tasks import ActionSubtask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_tool.tool import MockTool


class TestTextToolMemory:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.engines.PromptSummaryEngine.summarize_artifacts",
            return_value=TextArtifact("foobar summary")
        )

        mocker.patch(
            "griptape.engines.CsvExtractionEngine.extract",
            return_value=[CsvRowArtifact({"foo": "bar"})]
        )

    @pytest.fixture
    def memory(self):
        vector_store_driver = LocalVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver()
        )

        return TextToolMemory(
            name="MyMemory",
            query_engine=VectorQueryEngine(
                vector_store_driver=vector_store_driver
            )
        )

    def test_init(self, memory):
        assert memory.name == "MyMemory"

    def test_process_output(self, memory):
        artifact = TextArtifact("foo")
        subtask = ActionSubtask()

        assert memory.process_output(MockTool().test, subtask, artifact).to_text().startswith(
            'Output of "MockTool.test" was stored in memory'
        )
        assert memory.namespace_metadata[artifact.id] == subtask.action_to_json()

    def test_process_output_with_many_artifacts(self, memory):
        assert memory.process_output(MockTool().test, ActionSubtask(), [TextArtifact("foo")]).to_text().startswith(
            'Output of "MockTool.test" was stored in memory'
        )

    def test_upsert_namespace_artifact(self, memory):
        memory.query_engine.upsert_text_artifact(TextArtifact("foo"), namespace="test")

        assert len(memory.load_artifacts("test")) == 1

    def test_upsert_namespace_artifacts(self, memory):
        memory.query_engine.upsert_text_artifacts(
            [TextArtifact("foo"), TextArtifact("bar")],
            "test"
        )

        assert len(memory.load_artifacts("test")) == 2

    def test_load_artifacts(self, memory):
        memory.query_engine.upsert_text_artifacts(
            [TextArtifact("foo"), TextArtifact("bar")],
            "test"
        )

        assert len(memory.load_artifacts("test")) == 2

    def test_summarize(self, memory):
        assert memory.summarize(
            {"values": {"query": "foobar", "artifact_namespace": "foo"}}
        ).value == "foobar summary"

    def test_query(self, memory):
        assert memory.search(
            {"values": {"query": "foobar", "artifact_namespace": "foo"}}
        ).value == "foobar"
