from griptape.artifacts import TextArtifact, ListArtifact
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
            'Output of "MockTool.test" was stored in ramp "MyRamp" with the following artifact names'
        )

    def test_process_output_with_many_artifacts(self):
        ramp = TextStorageRamp(
            name="MyRamp",
            driver=MemoryTextStorageDriver()
        )

        assert ramp.process_output(MockTool().test, ListArtifact([TextArtifact("foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in ramp "MyRamp" with the following artifact names'
        )

    def test_save_and_load_value(self):
        ramp = TextStorageRamp()
        output = ramp.save_value({"values": {"artifact_value": "foobar"}})
        name = output.value.split(":")[-1].strip()

        assert ramp.load_value({"values": {"artifact_name": name}}).value == "foobar"
