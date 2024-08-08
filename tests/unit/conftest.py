import pytest

from griptape.events import EventBus


@pytest.fixture(autouse=True)
def event_bus():
    EventBus.clear_event_listeners()

    yield EventBus

    EventBus.clear_event_listeners()
