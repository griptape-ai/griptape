from griptape.artifacts import BlobArtifact, ListArtifact
from griptape.drivers import MemoryBlobStorageDriver
from griptape.memory.tool import BlobToolMemory
from tests.mocks.mock_tool.tool import MockTool


class TestBlobToolMemory:
    def test_init(self):
        memory = BlobToolMemory(driver=MemoryBlobStorageDriver())

        assert memory.name == BlobToolMemory.__name__

        memory = BlobToolMemory(name="MyMemory", driver=MemoryBlobStorageDriver())

        assert memory.name == "MyMemory"

    def test_process_output(self):
        memory = BlobToolMemory(name="MyMemory", driver=MemoryBlobStorageDriver())
        artifact = BlobArtifact(b"foo", name="foo")
        output = memory.process_output(MockTool().test, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names: foo'
        )

        assert memory.driver.load(artifact.full_path) == artifact

    def test_process_output_with_many_artifacts(self):
        memory = BlobToolMemory(name="MyMemory", driver=MemoryBlobStorageDriver())

        assert memory.process_output(MockTool().test, ListArtifact([BlobArtifact(b"foo", name="foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )
