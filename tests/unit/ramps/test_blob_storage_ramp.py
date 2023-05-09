from griptape.artifacts import BlobArtifact
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
        artifact = BlobArtifact("foo", value=b"foo")
        output = ramp.process_output(MockTool().test, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" as artifact'
        )

        assert ramp.driver.load(artifact.full_path) == artifact
