import pytest

from tests.mocks.mock_driver_config import MockDriverConfig


@pytest.fixture(autouse=True)
def mock_event_bus():
    from griptape.events import event_bus

    event_bus.clear_event_listeners()

    yield event_bus

    event_bus.clear_event_listeners()


@pytest.fixture(autouse=True)
def mock_config(request):
    from griptape.config import config

    # Some tests we don't want to use the autouse fixture's MockDriverConfig
    if "skip_mock_config" in request.keywords:
        yield

        return

    config.driver_config = MockDriverConfig()

    yield config
