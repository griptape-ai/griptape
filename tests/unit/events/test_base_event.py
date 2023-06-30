import pytest
from griptape.events import BaseEvent

class TestBaseEvent:
    @pytest.fixture
    def base_event(self):
        return BaseEvent()
