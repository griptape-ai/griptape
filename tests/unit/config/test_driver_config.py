import pytest

from griptape.config import DriverConfig


class TestDriverConfig:
    @pytest.fixture()
    def config(self):
        return DriverConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "DriverConfig",
            "prompt": {
                "type": "DummyPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "use_native_tools": False,
            },
            "conversation_memory": None,
            "embedding": {"type": "DummyEmbeddingDriver"},
            "image_generation": {"type": "DummyImageGenerationDriver"},
            "image_query": {"type": "DummyImageQueryDriver"},
            "vector_store": {
                "embedding_driver": {"type": "DummyEmbeddingDriver"},
                "type": "DummyVectorStoreDriver",
            },
            "text_to_speech": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert DriverConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_dot_update(self, config):
        config.prompt.max_tokens = 10

        assert config.prompt.max_tokens == 10
