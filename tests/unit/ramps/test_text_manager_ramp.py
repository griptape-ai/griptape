from griptape.artifacts import TextArtifact
from griptape.drivers import MemoryTextStorageDriver
from griptape.ramps import TextManagerRamp
from tests.mocks.mock_tool.tool import MockTool


class TestTextManagerRamp:
    def test_constructor(self):
        ramp = TextManagerRamp(
            name="MyRamp",
            driver=MemoryTextStorageDriver()
        )

        assert ramp.name == "MyRamp"

    def test_process_output(self):
        ramp = TextManagerRamp(
            name="MyRamp",
            driver=MemoryTextStorageDriver()
        )

        assert ramp.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with record ID'
        )
