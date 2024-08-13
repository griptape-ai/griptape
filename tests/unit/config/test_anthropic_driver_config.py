import pytest

from griptape.config import AnthropicDriverConfig


class TestAnthropicDriverConfig:
    @pytest.fixture(autouse=True)
    def _mock_anthropic(self, mocker):
        mocker.patch("anthropic.Anthropic")
        mocker.patch("voyageai.Client")

    @pytest.fixture()
    def config(self):
        return AnthropicDriverConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "AnthropicDriverConfig",
            "prompt": {
                "type": "AnthropicPromptDriver",
                "temperature": 0.1,
                "max_tokens": 1000,
                "stream": False,
                "model": "claude-3-5-sonnet-20240620",
                "top_p": 0.999,
                "top_k": 250,
                "use_native_tools": True,
            },
            "image_generation": {"type": "DummyImageGenerationDriver"},
            "image_query": {
                "type": "AnthropicImageQueryDriver",
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 256,
            },
            "embedding": {
                "type": "VoyageAiEmbeddingDriver",
                "model": "voyage-large-2",
                "input_type": "document",
            },
            "vector_store": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "VoyageAiEmbeddingDriver",
                    "model": "voyage-large-2",
                    "input_type": "document",
                },
            },
            "conversation_memory": None,
            "text_to_speech": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert AnthropicDriverConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
