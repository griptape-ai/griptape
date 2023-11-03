import pytest
from griptape.events import FinishStructureRunEvent


class TestFinishStructureRunEvent:
    @pytest.fixture
    def finish_structure_run_event(self):
        return FinishStructureRunEvent()

    def test_to_dict(self, finish_structure_run_event):
        assert finish_structure_run_event.to_dict() is not None
