import pytest

from griptape.config import GoogleStructureConfig


class TestGoogleStructureConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("google.generativeai.GenerativeModel")

    @pytest.fixture()
    def config(self):
        return GoogleStructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "GoogleStructureConfig",
            "prompt_driver": {
                "type": "GooglePromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "model": "gemini-1.5-pro",
                "top_p": None,
                "top_k": None,
                "tool_choice": "auto",
                "use_native_tools": True,
            },
            "image_generation_driver": {"type": "DummyImageGenerationDriver"},
            "embedding_driver": {
                "type": "GoogleEmbeddingDriver",
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "title": None,
            },
            "vector_store_driver": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "GoogleEmbeddingDriver",
                    "model": "models/embedding-001",
                    "task_type": "retrieval_document",
                    "title": None,
                },
            },
            "conversation_memory_driver": None,
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert GoogleStructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
