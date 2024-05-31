from pytest import fixture
from griptape.config import OpenAiStructureConfig


class TestOpenAiStructureConfig:
    @fixture(autouse=True)
    def mock_openai(self, mocker):
        return mocker.patch("openai.OpenAI")

    @fixture
    def config(self):
        return OpenAiStructureConfig(api_key="api_key", base_url="foo", organization="bar")

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "OpenAiStructureConfig",
            "prompt_driver": {
                "type": "OpenAiChatPromptDriver",
                "base_url": "foo",
                "model": "gpt-4o",
                "organization": "bar",
                "response_format": None,
                "seed": None,
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
                "user": "",
            },
            "base_url": "foo",
            "organization": "bar",
            "conversation_memory_driver": None,
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
            "embedding_driver": {
                "base_url": "foo",
                "model": "text-embedding-3-small",
                "organization": "bar",
                "type": "OpenAiEmbeddingDriver",
            },
            "image_generation_driver": {
                "api_version": None,
                "base_url": "foo",
                "image_size": "512x512",
                "model": "dall-e-2",
                "organization": "bar",
                "quality": "standard",
                "response_format": "b64_json",
                "style": None,
                "type": "OpenAiImageGenerationDriver",
            },
            "image_query_driver": {
                "api_version": None,
                "base_url": "foo",
                "image_quality": "auto",
                "max_tokens": 256,
                "model": "gpt-4o",
                "organization": "bar",
                "type": "OpenAiImageQueryDriver",
            },
            "vector_store_driver": {
                "embedding_driver": {
                    "base_url": "foo",
                    "model": "text-embedding-3-small",
                    "organization": "bar",
                    "type": "OpenAiEmbeddingDriver",
                },
                "type": "LocalVectorStoreDriver",
            },
        }

    def test_from_dict(self):
        config = OpenAiStructureConfig.from_dict({"api_key": "api_key", "base_url": "foo", "organization": "bar"})
        assert config.api_key == "api_key"
        assert config.base_url == "foo"
        assert config.organization == "bar"

        assert config.prompt_driver.api_key == "api_key"
        assert config.prompt_driver.base_url == "foo"
        assert config.prompt_driver.organization == "bar"
        assert config.prompt_driver.model == "gpt-4o"

        # Top level fields will not be used if you override the Driver
        config = OpenAiStructureConfig.from_dict(
            {
                "api_key": "api_key",
                "base_url": "foo",
                "organization": "bar",
                "prompt_driver": {"type": "OpenAiChatPromptDriver", "model": "foo bar"},
            }
        )
        assert config.api_key == "api_key"
        assert config.base_url == "foo"
        assert config.organization == "bar"

        assert config.prompt_driver.api_key is None
        assert config.prompt_driver.base_url is None
        assert config.prompt_driver.organization is None
        assert config.prompt_driver.model == "foo bar"
