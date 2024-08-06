import pytest

from griptape.config import AzureOpenAiDriverConfig


class TestAzureOpenAiDriverConfig:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("openai.AzureOpenAI")

    @pytest.fixture()
    def config(self):
        return AzureOpenAiDriverConfig(
            azure_endpoint="http://localhost:8080",
            azure_ad_token="test-token",
            azure_ad_token_provider=lambda: "test-provider",
        )

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "AzureOpenAiDriverConfig",
            "azure_endpoint": "http://localhost:8080",
            "prompt": {
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
            "conversation_memory": None,
            "embedding": {
                "base_url": None,
                "model": "text-embedding-3-small",
                "api_version": "2023-05-15",
                "azure_deployment": "text-embedding-3-small",
                "azure_endpoint": "http://localhost:8080",
                "organization": None,
                "type": "AzureOpenAiEmbeddingDriver",
            },
            "image_generation": {
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
            "image_query": {
                "base_url": None,
                "image_quality": "auto",
                "max_tokens": 256,
                "model": "gpt-4o",
                "api_version": "2024-02-01",
                "azure_deployment": "gpt-4o",
                "azure_endpoint": "http://localhost:8080",
                "organization": None,
                "type": "AzureOpenAiImageQueryDriver",
            },
            "vector_store": {
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
            "text_to_speech": {"type": "DummyTextToSpeechDriver"},
            "audio_transcription": {"type": "DummyAudioTranscriptionDriver"},
        }
