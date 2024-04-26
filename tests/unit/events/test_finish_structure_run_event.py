import pytest
from griptape.artifacts.text_artifact import TextArtifact
from griptape.events import FinishStructureRunEvent


class TestFinishStructureRunEvent:
    @pytest.fixture
    def finish_structure_run_event(self):
        return FinishStructureRunEvent(output_task_input=TextArtifact("foo"), output_task_output=TextArtifact("bar"))

    def test_to_dict(self, finish_structure_run_event):
        assert finish_structure_run_event.to_dict() is not None

        assert finish_structure_run_event.to_dict()["output_task_input"]["value"] == "foo"
        assert finish_structure_run_event.to_dict()["output_task_output"]["value"] == "bar"
