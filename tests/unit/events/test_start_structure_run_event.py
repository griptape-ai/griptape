import pytest
from griptape.artifacts.text_artifact import TextArtifact
from griptape.events import StartStructureRunEvent


class TestStartStructureRunEvent:
    @pytest.fixture
    def start_structure_run_event(self):
        return StartStructureRunEvent(input_task_input=TextArtifact("foo"), input_task_output=TextArtifact("bar"))

    def test_to_dict(self, start_structure_run_event):
        assert start_structure_run_event.to_dict() is not None
        assert start_structure_run_event.to_dict()["input_task_input"]["value"] == "foo"
        assert start_structure_run_event.to_dict()["input_task_output"]["value"] == "bar"
