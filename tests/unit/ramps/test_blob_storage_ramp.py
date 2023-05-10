from griptape.artifacts import BlobArtifact, ListArtifact
from griptape.drivers import MemoryBlobStorageDriver
from griptape.ramps import BlobStorageRamp
from tests.mocks.mock_tool.tool import MockTool


class TestBlobStorageRamp:
    def test_constructor(self):
        ramp = BlobStorageRamp(driver=MemoryBlobStorageDriver())

        assert ramp.name == BlobStorageRamp.__name__

        ramp = BlobStorageRamp(name="MyRamp", driver=MemoryBlobStorageDriver())

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = BlobStorageRamp(name="MyRamp", driver=MemoryBlobStorageDriver())
        artifact = BlobArtifact(b"foo", name="foo")
        output = ramp.process_output(MockTool().test, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with the following artifact names: foo'
        )

        assert ramp.driver.load(artifact.full_path) == artifact

    def test_process_output_with_many_artifacts(self):
        ramp = BlobStorageRamp(name="MyRamp", driver=MemoryBlobStorageDriver())

        assert ramp.process_output(MockTool().test, ListArtifact([BlobArtifact(b"foo", name="foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with the following artifact names'
        )
