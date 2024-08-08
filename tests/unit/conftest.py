import pytest

from griptape.events import event_bus


@pytest.fixture(autouse=True)
def mock_event_bus():
    event_bus.clear_event_listeners()

    yield event_bus

    event_bus.clear_event_listeners()
