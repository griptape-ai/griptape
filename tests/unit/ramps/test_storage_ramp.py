from griptape.artifacts import TextArtifact
from griptape.drivers import MemoryStorageDriver
from griptape.ramps import StorageRamp
from tests.mocks.mock_tool.tool import MockTool


class TestStorageRamp:
    def test_constructor(self):
        ramp = StorageRamp(
            driver=MemoryStorageDriver()
        )

        assert ramp.name == "StorageRamp"

        ramp = StorageRamp(
            name="MyRamp",
            driver=MemoryStorageDriver()
        )

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = StorageRamp(
            name="MyRamp",
            driver=MemoryStorageDriver()
        )

        assert ramp.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with entry ID'
        )
