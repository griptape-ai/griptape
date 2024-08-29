import pytest

from griptape.configs.drivers import CohereDriversConfig


class TestCohereDriversConfig:
    @pytest.fixture()
    def config(self):
        return CohereDriversConfig(api_key="api_key")

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "CohereDriversConfig",
            "image_generation_driver": {"type": "DummyImageGenerationDriver"},
            "image_query_driver": {"type": "DummyImageQueryDriver"},
            "conversation_memory_driver": {
                "type": "LocalConversationMemoryDriver",
                "persist_file": None,
            },
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
            "prompt_driver": {
                "type": "CoherePromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "model": "command-r",
                "force_single_step": False,
                "use_native_tools": True,
            },
            "embedding_driver": {
                "type": "CohereEmbeddingDriver",
                "model": "embed-english-v3.0",
                "input_type": "search_document",
            },
            "vector_store_driver": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "CohereEmbeddingDriver",
                    "model": "embed-english-v3.0",
                    "input_type": "search_document",
                },
            },
        }
