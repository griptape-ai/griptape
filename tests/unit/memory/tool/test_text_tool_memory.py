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
            name="MyMemory",
            query_engine=query_engine
        )

    def test_init(self, memory):
        assert memory.name == "MyMemory"

    def test_allowlist(self):
        assert len(TextToolMemory().activities()) == 1
        assert TextToolMemory().activities()[0].__name__ == "save"

    def test_process_output(self, memory):
        assert memory.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )

    def test_process_output_with_many_artifacts(self, memory):
        assert memory.process_output(MockTool().test, ListArtifact([TextArtifact("foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )

    def test_save_and_load_value(self):
        memory = TextToolMemory()
        output = memory.save({"values": {"artifact_value": "foobar"}})
        name = output.value.split(":")[-1].strip()

        assert memory.load({"values": {"artifact_namespace": name}}).value[0].value == "foobar"

