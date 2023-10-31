import pytest
from griptape.events import StartStructureRunEvent


class TestStartStructureRunEvent:
    @pytest.fixture
    def start_structure_run_event(self):
        return StartStructureRunEvent()

    def test_to_dict(self, start_structure_run_event):
        assert start_structure_run_event.to_dict() is not None
