import pytest

from griptape.config import StructureConfig


class TestStructureConfig:
    @pytest.fixture()
    def config(self):
        return StructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "StructureConfig",
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
        assert StructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_unchanged_merge_config(self, config):
        assert (
            config.merge_config(
                {
                    "type": "StructureConfig",
                    "prompt_driver": {
                        "type": "DummyPromptDriver",
                        "temperature": 0.1,
                        "max_tokens": None,
                        "stream": False,
                    },
                }
            ).to_dict()
            == config.to_dict()
        )

    def test_changed_merge_config(self, config):
        config = config.merge_config(
            {"prompt_driver": {"type": "DummyPromptDriver", "temperature": 0.1, "max_tokens": None, "stream": False}}
        )

        assert config.prompt_driver.temperature == 0.1

    def test_dot_update(self, config):
        config.prompt_driver.max_tokens = 10

        assert config.prompt_driver.max_tokens == 10
