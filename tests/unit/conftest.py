import pytest

from griptape.config import Config
from tests.mocks.mock_driver_config import MockDriverConfig


@pytest.fixture(autouse=True)
def mock_config():
    Config.drivers = MockDriverConfig()

    return Config
