import pytest

from griptape.config import StructureConfig
from griptape.structures import Agent


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

    def test_drivers(self, config):
        assert config.drivers == [
            config.prompt_driver,
            config.image_generation_driver,
            config.embedding_driver,
            config.vector_store_driver,
            config.conversation_memory_driver,
            config.text_to_speech_driver,
            config.audio_transcription_driver,
        ]

    def test_structure(self, config):
        structure_1 = Agent(
            config=config,
        )

        assert config.structure == structure_1
        assert config._event_listener is not None
        for driver in config.drivers:
            if driver is not None:
                assert config._event_listener in driver.event_listeners
                assert len(driver.event_listeners) == 1

        structure_2 = Agent(
            config=config,
        )
        assert config.structure == structure_2
        assert config._event_listener is not None
        for driver in config.drivers:
            if driver is not None:
                assert config._event_listener in driver.event_listeners
                assert len(driver.event_listeners) == 1
