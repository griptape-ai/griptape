import pytest
from griptape.artifacts import BlobArtifact
from griptape.drivers import LocalBlobToolMemoryDriver
from griptape.memory.tool import BlobToolMemory
from griptape.tasks import ActionSubtask
from tests.mocks.mock_tool.tool import MockTool


class TestBlobToolMemory:
    @pytest.fixture
    def memory(self):
        return BlobToolMemory(
            id="MyMemory",
            driver=LocalBlobToolMemoryDriver()
        )

    def test_init(self, memory):
        assert memory.id == "MyMemory"

        memory = BlobToolMemory(driver=LocalBlobToolMemoryDriver())

        assert memory.id == BlobToolMemory.__name__

    def test_process_output(self, memory):
        artifact = BlobArtifact(b"foo", name="foo")
        subtask = ActionSubtask()
        output = memory.process_output(MockTool().test, subtask, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )
        assert memory.namespace_metadata[artifact.id] == subtask.to_json()

        assert memory.driver.load(artifact.id) == [artifact]

    def test_process_output_with_many_artifacts(self, memory):
        assert memory.process_output(
            MockTool().test, ActionSubtask(), [BlobArtifact(b"foo", name="foo")]
        ).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact namespace:'
        )

    def test_load_artifacts(self, memory):
        for a in [BlobArtifact(b"foo", name="fooname"), BlobArtifact(b"bar", name="barname")]:
            memory.driver.save("test", a)

        assert len(memory.load_artifacts("test")) == 2
