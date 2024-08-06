import pytest

from griptape.config import Config
from griptape.events import EventBus
from tests.mocks.mock_driver_config import MockDriverConfig


@pytest.fixture(autouse=True)
def event_bus():
    EventBus.event_listeners = []

    yield EventBus

    EventBus.event_listeners = []


@pytest.fixture(autouse=True)
def mock_config():
    Config.drivers = MockDriverConfig()

    return Config
