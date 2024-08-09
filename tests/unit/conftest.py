import pytest

from griptape.config import config
from griptape.events import event_bus
from tests.mocks.mock_driver_config import MockDriverConfig


@pytest.fixture(autouse=True)
def mock_event_bus():
    event_bus.clear_event_listeners()

    yield event_bus

    event_bus.clear_event_listeners()


@pytest.fixture(autouse=True)
def mock_config():
    config.drivers = MockDriverConfig()

    return config
