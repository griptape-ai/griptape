import pytest

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.events import FinishStructureRunEvent


class TestFinishStructureRunEvent:
    @pytest.fixture()
    def finish_structure_run_event(self):
        return FinishStructureRunEvent(
            structure_id="fizz",
            output_task_input=ListArtifact(
                [TextArtifact("foo"), ImageArtifact(b"", format="png", width=100, height=100)]
            ),
            output_task_output=TextArtifact("bar"),
        )

    def test_to_dict(self, finish_structure_run_event):
        assert finish_structure_run_event.to_dict() is not None

        assert finish_structure_run_event.to_dict()["structure_id"] == "fizz"
        assert finish_structure_run_event.to_dict()["output_task_input"]["value"][0]["value"] == "foo"
        assert finish_structure_run_event.to_dict()["output_task_output"]["value"] == "bar"

    def test_from_dict(self, finish_structure_run_event):
        assert FinishStructureRunEvent.from_dict(finish_structure_run_event.to_dict()) == finish_structure_run_event
