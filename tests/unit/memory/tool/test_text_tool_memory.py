import pytest
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import MemoryVectorDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_tool.tool import MockTool


class TestTextToolMemory:
    @pytest.fixture
    def memory(self):
        query_engine = VectorQueryEngine(
            vector_driver=MemoryVectorDriver(
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
        assert memory.process_output(MockTool().test, ListArtifact([TextArtifact("foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )
