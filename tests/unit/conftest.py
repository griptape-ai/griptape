import os
from io import BytesIO, StringIO
from pathlib import Path

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


@pytest.fixture()
def path_from_resource_path():
    def create_source(resource_path: str) -> Path:
        return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources", resource_path))

    return create_source


@pytest.fixture()
def bytes_from_resource_path(path_from_resource_path):
    def create_source(resource_path: str) -> BytesIO:
        return BytesIO(Path(path_from_resource_path(resource_path)).read_bytes())

    return create_source


@pytest.fixture()
def str_from_resource_path(path_from_resource_path):
    def test_csv_str(resource_path: str) -> StringIO:
        return StringIO(Path(path_from_resource_path(resource_path)).read_text())

    return test_csv_str
