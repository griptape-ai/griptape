from griptape.artifacts import BlobArtifact, ListArtifact
from griptape.drivers import MemoryBlobStorageDriver
from griptape.memory.tool import BlobMemory
from tests.mocks.mock_tool.tool import MockTool


class TestBlobMemory:
    def test_constructor(self):
        memory = BlobMemory(driver=MemoryBlobStorageDriver())

        assert memory.name == BlobMemory.__name__

        memory = BlobMemory(name="MyMemory", driver=MemoryBlobStorageDriver())

        assert memory.name == "MyMemory"

    def test_process_output(self):
        memory = BlobMemory(name="MyMemory", driver=MemoryBlobStorageDriver())
        artifact = BlobArtifact(b"foo", name="foo")
        output = memory.process_output(MockTool().test, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names: foo'
        )

        assert memory.driver.load(artifact.full_path) == artifact

    def test_process_output_with_many_artifacts(self):
        memory = BlobMemory(name="MyMemory", driver=MemoryBlobStorageDriver())

        assert memory.process_output(MockTool().test, ListArtifact([BlobArtifact(b"foo", name="foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )
