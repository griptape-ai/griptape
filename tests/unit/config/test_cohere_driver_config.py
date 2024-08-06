import pytest

from griptape.config import CohereDriverConfig


class TestCohereDriverConfig:
    @pytest.fixture()
    def config(self):
        return CohereDriverConfig(api_key="api_key")

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "CohereDriverConfig",
            "image_generation": {"type": "DummyImageGenerationDriver"},
            "image_query": {"type": "DummyImageQueryDriver"},
            "conversation_memory": None,
            "text_to_speech": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription": {"type": "DummyAudioTranscriptionDriver"},
            "prompt": {
                "type": "CoherePromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "model": "command-r",
                "force_single_step": False,
                "use_native_tools": True,
            },
            "embedding": {
                "type": "CohereEmbeddingDriver",
                "model": "embed-english-v3.0",
                "input_type": "search_document",
            },
            "vector_store": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "CohereEmbeddingDriver",
                    "model": "embed-english-v3.0",
                    "input_type": "search_document",
                },
            },
        }
