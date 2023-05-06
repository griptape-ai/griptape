from griptape.artifacts import TextArtifact
from griptape.drivers import MemoryStorageDriver
from griptape.ramps import StorageRamp
from tests.mocks.mock_tool.tool import MockTool


class TestStorageRamp:
    def test_constructor(self):
        mw = StorageRamp(
            driver=MemoryStorageDriver()
        )

        assert mw.name == "StorageRamp"

        mw = StorageRamp(
            name="MyRamp",
            driver=MemoryStorageDriver()
        )

        assert mw.name == "MyRamp"

    def test_process_output(self):
        mw = StorageRamp(
            name="MyRamp",
            driver=MemoryStorageDriver()
        )

        assert mw.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with entry ID'
        )
