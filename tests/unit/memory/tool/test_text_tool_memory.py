from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import MemoryTextStorageDriver
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_tool.tool import MockTool


class TestTextToolMemory:
    def test_init(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextStorageDriver()
        )

        assert memory.name == "MyMemory"

    def test_process_output(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextStorageDriver()
        )

        assert memory.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )

    def test_process_output_with_many_artifacts(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextStorageDriver()
        )

        assert memory.process_output(MockTool().test, ListArtifact([TextArtifact("foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )

    def test_save_and_load_value(self):
        memory = TextToolMemory()
        output = memory.save({"values": {"artifact_value": "foobar"}})
        name = output.value.split(":")[-1].strip()

        assert memory.load({"values": {"artifact_name": name}}).value == "foobar"
