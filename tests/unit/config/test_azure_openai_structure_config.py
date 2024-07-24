import pytest

from griptape.config import AzureOpenAiStructureConfig


class TestAzureOpenAiStructureConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("openai.AzureOpenAI")

    @pytest.fixture()
    def config(self):
        return AzureOpenAiStructureConfig(
            azure_endpoint="http://localhost:8080",
            azure_ad_token="test-token",
            azure_ad_token_provider=lambda: "test-provider",
        )

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "AzureOpenAiStructureConfig",
            "azure_endpoint": "http://localhost:8080",
            "prompt_driver": {
                "type": "AzureOpenAiChatPromptDriver",
                "base_url": None,
                "model": "gpt-4o",
                "azure_deployment": "gpt-4o",
                "azure_endpoint": "http://localhost:8080",
                "api_version": "2023-05-15",
                "organization": None,
                "response_format": None,
                "seed": None,
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "user": "",
                "use_native_tools": True,
            },
            "conversation_memory_driver": None,
            "embedding_driver": {
                "base_url": None,
                "model": "text-embedding-3-small",
                "api_version": "2023-05-15",
                "azure_deployment": "text-embedding-3-small",
                "azure_endpoint": "http://localhost:8080",
                "organization": None,
                "type": "AzureOpenAiEmbeddingDriver",
            },
            "image_generation_driver": {
                "api_version": "2024-02-01",
                "base_url": None,
                "image_size": "512x512",
                "model": "dall-e-2",
                "azure_deployment": "dall-e-2",
                "azure_endpoint": "http://localhost:8080",
                "organization": None,
                "quality": "standard",
                "response_format": "b64_json",
                "style": None,
                "type": "AzureOpenAiImageGenerationDriver",
            },
            "vector_store_driver": {
                "embedding_driver": {
                    "base_url": None,
                    "model": "text-embedding-3-small",
                    "api_version": "2023-05-15",
                    "azure_deployment": "text-embedding-3-small",
                    "azure_endpoint": "http://localhost:8080",
                    "organization": None,
                    "type": "AzureOpenAiEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription_driver": {"type": "DummyAudioTranscriptionDriver"},
        }

    def test_from_dict(self, config: AzureOpenAiStructureConfig):
        assert AzureOpenAiStructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

        # override values in the dict config
        # serialize and deserialize the config
        new_config = config.merge_config(
            {
                "prompt_driver": {"azure_deployment": "new-test-gpt-4"},
                "embedding_driver": {"model": "new-text-embedding-3-small"},
            }
        ).to_dict()
        assert AzureOpenAiStructureConfig.from_dict(new_config).to_dict() == new_config
