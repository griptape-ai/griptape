from griptape.artifacts import BlobArtifact
from griptape.drivers import MemoryBlobStorageDriver
from griptape.ramps import BlobManagerRamp
from tests.mocks.mock_tool.tool import MockTool


class TestBlobManagerRamp:
    def test_constructor(self):
        ramp = BlobManagerRamp(driver=MemoryBlobStorageDriver())

        assert ramp.name == "BlobManagerRamp"

        ramp = BlobManagerRamp(name="MyRamp", driver=MemoryBlobStorageDriver())

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = BlobManagerRamp(name="MyRamp", driver=MemoryBlobStorageDriver())
        artifact = BlobArtifact("foo", value=b"foo")
        output = ramp.process_output(MockTool().test, artifact)

        assert output.to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" as artifact'
        )

        assert ramp.driver.load(artifact.full_path) == artifact
