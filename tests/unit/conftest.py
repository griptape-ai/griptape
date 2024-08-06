import pytest

from griptape.config import Config
from griptape.events import EventBus
from tests.mocks.mock_structure_config import MockStructureConfig


@pytest.fixture(autouse=True)
def event_bus():
    EventBus.event_listeners = []

    yield EventBus

    EventBus.event_listeners = []


@pytest.fixture(autouse=True)
def mock_config():
    mock_structure_config = MockStructureConfig()
    Config.prompt_driver = mock_structure_config.prompt_driver
    Config.image_generation_driver = mock_structure_config.image_generation_driver
    Config.image_query_driver = mock_structure_config.image_query_driver
    Config.embedding_driver = mock_structure_config.embedding_driver
    Config.vector_store_driver = mock_structure_config.vector_store_driver
    Config.text_to_speech_driver = mock_structure_config.text_to_speech_driver
    Config.audio_transcription_driver = mock_structure_config.audio_transcription_driver

    return Config
