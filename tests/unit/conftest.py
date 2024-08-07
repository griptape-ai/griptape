import pytest

from griptape.events import EventBus


@pytest.fixture(autouse=True)
def event_bus():
    EventBus.event_listeners = []

    yield EventBus

    EventBus.event_listeners = []
