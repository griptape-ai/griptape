from griptape.artifacts import TextArtifact
from griptape.drivers import MemoryTextStorageDriver
from griptape.ramps import TextStorageRamp
from tests.mocks.mock_tool.tool import MockTool


class TestTextStorageRamp:
    def test_constructor(self):
        ramp = TextStorageRamp(
            name="MyRamp",
            driver=MemoryTextStorageDriver()
        )

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = TextStorageRamp(
            name="MyRamp",
            driver=MemoryTextStorageDriver()
        )

        assert ramp.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with artifact ID'
        )
