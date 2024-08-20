import pytest

from tests.mocks.mock_drivers_config import MockDriversConfig


@pytest.fixture(autouse=True)
def mock_event_bus():
    from griptape.events import event_bus

    event_bus.clear_event_listeners()

    yield event_bus

    event_bus.clear_event_listeners()


@pytest.fixture(autouse=True)
def mock_config(request):
    from griptape.configs import config

    # Some tests we don't want to use the autouse fixture's MockDriversConfig
    if "skip_mock_config" in request.keywords:
        yield

        return

    config.drivers_config = MockDriversConfig()

    yield config
