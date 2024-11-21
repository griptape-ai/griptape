import os
from unittest import mock

import pytest

from tests.mocks.mock_drivers_config import MockDriversConfig


@pytest.fixture(autouse=True)
def mock_event_bus():
    from griptape.events import EventBus

    EventBus.clear_event_listeners()

    yield EventBus

    EventBus.clear_event_listeners()


@pytest.fixture(autouse=True)
def mock_config(request):
    from griptape.configs import Defaults

    # Some tests we don't want to use the autouse fixture's MockDriversConfig
    if "skip_mock_config" in request.keywords:
        yield

        return

    Defaults.drivers_config = MockDriversConfig()

    yield Defaults


@pytest.fixture(autouse=True)
def _mock_env():
    # removing env vars on Windows causes requests to error with [Errno 11001]
    if os.name == "nt":
        yield
    else:
        with mock.patch.dict(os.environ, clear=True):
            yield
