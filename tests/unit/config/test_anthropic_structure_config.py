from pytest import fixture
from griptape.config import AnthropicStructureConfig


class TestAnthropicStructureConfig:
    @fixture(autouse=True)
    def mock_anthropic(self, mocker):
        mocker.patch("anthropic.Anthropic")
        mocker.patch("voyageai.Client")

    @fixture
    def config(self):
        return AnthropicStructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "AnthropicStructureConfig",
            "prompt_driver": {
                "type": "AnthropicPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "model": "claude-3-opus-20240229",
                "top_p": 0.999,
                "top_k": 250,
            },
            "image_generation_driver": {"type": "DummyImageGenerationDriver"},
            "image_query_driver": {
                "type": "AnthropicImageQueryDriver",
                "model": "claude-3-opus-20240229",
                "max_tokens": 256,
            },
            "embedding_driver": {
                "type": "VoyageAiEmbeddingDriver",
                "model": "voyage-large-2",
                "input_type": "document",
            },
            "vector_store_driver": {
                "type": "LocalVectorStoreDriver",
                "embedding_driver": {
                    "type": "VoyageAiEmbeddingDriver",
                    "model": "voyage-large-2",
                    "input_type": "document",
                },
            },
            "conversation_memory_driver": None,
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config):
        assert AnthropicStructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()
