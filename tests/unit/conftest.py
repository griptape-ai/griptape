import pytest

from griptape.config import Config
from tests.mocks.mock_structure_config import MockStructureConfig


@pytest.fixture(autouse=True)
def mock_config():
    Config.drivers = MockStructureConfig()

    return Config
