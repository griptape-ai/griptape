import pytest

from griptape.config import GoogleDriverConfig


class TestGoogleStructureConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("google.generativeai.GenerativeModel")

    @pytest.fixture()
    def config(self):
        return GoogleDriverConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "GoogleDriverConfig",
            "prompt": {
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
            "image_generation": {"type": "DummyImageGenerationDriver"},
            "image_query": {"type": "DummyImageQueryDriver"},
            "embedding": {
                "type": "GoogleEmbeddingDriver",
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "title": None,
            },
            "vector_store": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "GoogleEmbeddingDriver",
                    "model": "models/embedding-001",
                    "task_type": "retrieval_document",
                    "title": None,
                },
            },
            "conversation_memory": None,
            "text_to_speech": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert GoogleDriverConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
