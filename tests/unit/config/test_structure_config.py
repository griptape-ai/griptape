from pytest import fixture
from tests.mocks.mock_structure_config import MockStructureConfig


class TestStructureConfig:
    @fixture
    def config(self):
        return MockStructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "MockStructureConfig",
            "overrides": {},
            "prompt_driver": {"type": "MockPromptDriver", "temperature": 0.1, "max_tokens": None, "stream": False},
            "conversation_memory_driver": None,
            "embedding_driver": {"type": "MockEmbeddingDriver"},
            "image_generation_driver": {"type": "MockImageGenerationDriver", "model": "dall-e-2"},
            "image_query_driver": {"type": "MockImageQueryDriver", "max_tokens": 256},
            "vector_store_driver": {
                "embedding_driver": {"type": "DummyEmbeddingDriver"},
                "type": "DummyVectorStoreDriver",
            },
            "text_to_speech_driver": {"type": "DummyTextToSpeechDriver"},
        }

    def test_changed_merge_config(self, config):
        config = MockStructureConfig(
            overrides={
                "prompt_driver": {"type": "DummyPromptDriver", "temperature": 0.1, "max_tokens": None, "stream": False}
            }
        )

        assert config.prompt_driver.temperature == 0.1

    def test_dot_update(self, config):
        config.prompt_driver.max_tokens = 10

        assert config.prompt_driver.max_tokens == 10
