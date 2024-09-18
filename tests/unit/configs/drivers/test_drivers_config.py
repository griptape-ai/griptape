import pytest

from griptape.configs.drivers import DriversConfig
from tests.mocks.mock_drivers_config import MockDriversConfig


class TestDriversConfig:
    @pytest.fixture()
    def config(self):
        return DriversConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "DriversConfig",
            "prompt_driver": {
                "type": "DummyPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "use_native_tools": False,
            },
            "conversation_memory_driver": {
                "type": "LocalConversationMemoryDriver",
                "persist_file": None,
            },
            "embedding_driver": {"type": "DummyEmbeddingDriver"},
            "image_generation_driver": {"type": "DummyImageGenerationDriver"},
            "image_query_driver": {"type": "DummyImageQueryDriver"},
            "vector_store_driver": {
                "embedding_driver": {"type": "DummyEmbeddingDriver"},
                "type": "DummyVectorStoreDriver",
            },
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert DriversConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_dot_update(self, config):
        config.prompt_driver.max_tokens = 10

        assert config.prompt_driver.max_tokens == 10

    def test_context_manager(self):
        from griptape.configs import Defaults

        old_drivers_config = Defaults.drivers_config

        with MockDriversConfig() as config:
            assert Defaults.drivers_config == config

        assert Defaults.drivers_config == old_drivers_config

    @pytest.mark.skip_mock_config()
    def test_lazy_init(self):
        from griptape.configs import Defaults

        assert Defaults.drivers_config._prompt_driver is None
        assert Defaults.drivers_config._image_generation_driver is None
        assert Defaults.drivers_config._image_query_driver is None
        assert Defaults.drivers_config._embedding_driver is None
        assert Defaults.drivers_config._vector_store_driver is None
        assert Defaults.drivers_config._conversation_memory_driver is None
        assert Defaults.drivers_config._text_to_speech_driver is None
        assert Defaults.drivers_config._audio_transcription_driver is None

        assert Defaults.drivers_config.prompt_driver is not None
        assert Defaults.drivers_config.image_generation_driver is not None
        assert Defaults.drivers_config.image_query_driver is not None
        assert Defaults.drivers_config.embedding_driver is not None
        assert Defaults.drivers_config.vector_store_driver is not None
        assert Defaults.drivers_config.conversation_memory_driver is not None
        assert Defaults.drivers_config.text_to_speech_driver is not None
        assert Defaults.drivers_config.audio_transcription_driver is not None

        assert Defaults.drivers_config._prompt_driver is not None
        assert Defaults.drivers_config._image_generation_driver is not None
        assert Defaults.drivers_config._image_query_driver is not None
        assert Defaults.drivers_config._embedding_driver is not None
        assert Defaults.drivers_config._vector_store_driver is not None
        assert Defaults.drivers_config._conversation_memory_driver is not None
        assert Defaults.drivers_config._text_to_speech_driver is not None
        assert Defaults.drivers_config._audio_transcription_driver is not None
