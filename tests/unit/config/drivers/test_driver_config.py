import pytest

from griptape.config.drivers import DriverConfig


class TestDriverConfig:
    @pytest.fixture()
    def config(self):
        return DriverConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "DriverConfig",
            "prompt_driver": {
                "type": "DummyPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "use_native_tools": False,
            },
            "conversation_memory_driver": None,
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
        assert DriverConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_dot_update(self, config):
        config.prompt_driver.max_tokens = 10

        assert config.prompt_driver.max_tokens == 10

    @pytest.mark.skip_mock_config()
    def test_lazy_init(self):
        from griptape.config import config

        assert config.driver_config._prompt_driver is None
        assert config.driver_config._image_generation_driver is None
        assert config.driver_config._image_query_driver is None
        assert config.driver_config._embedding_driver is None
        assert config.driver_config._vector_store_driver is None
        assert config.driver_config._conversation_memory_driver is None
        assert config.driver_config._text_to_speech_driver is None
        assert config.driver_config._audio_transcription_driver is None

        assert config.driver_config.prompt_driver is not None
        assert config.driver_config.image_generation_driver is not None
        assert config.driver_config.image_query_driver is not None
        assert config.driver_config.embedding_driver is not None
        assert config.driver_config.vector_store_driver is not None
        assert config.driver_config.conversation_memory_driver is None
        assert config.driver_config.text_to_speech_driver is not None
        assert config.driver_config.audio_transcription_driver is not None

        assert config.driver_config._prompt_driver is not None
        assert config.driver_config._image_generation_driver is not None
        assert config.driver_config._image_query_driver is not None
        assert config.driver_config._embedding_driver is not None
        assert config.driver_config._vector_store_driver is not None
        assert config.driver_config._conversation_memory_driver is None
        assert config.driver_config._text_to_speech_driver is not None
        assert config.driver_config._audio_transcription_driver is not None
