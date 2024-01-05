from griptape.config import OpenAiStructureConfig
from griptape.config.base_structure_config import BaseStructureConfig


class TestOpenAiStructureConfig:
    def test_to_dict(self):
        config = OpenAiStructureConfig()

        result = config.to_dict()

        assert result == {
            "type": "OpenAiStructureConfig",
            "prompt_driver": {
                "type": "OpenAiChatPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "model": "gpt-4",
                "stream": False,
            },
            "task_memory": {
                "type": "StructureTaskMemoryConfig",
                "query_engine": {
                    "type": "StructureTaskMemoryQueryEngineConfig",
                    "prompt_driver": {
                        "type": "OpenAiChatPromptDriver",
                        "temperature": 0.1,
                        "max_tokens": None,
                        "model": "gpt-3.5-turbo-16k",
                        "stream": False,
                    },
                    "vector_store_driver": {
                        "type": "LocalVectorStoreDriver",
                        "embedding_driver": {"type": "OpenAiEmbeddingDriver", "model": "text-embedding-ada-002"},
                    },
                },
                "extraction_engine": {
                    "type": "StructureTaskMemoryExtractionEngineConfig",
                    "csv": {
                        "type": "StructureTaskMemoryExtractionEngineCsvConfig",
                        "prompt_driver": {
                            "type": "OpenAiChatPromptDriver",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "model": "gpt-3.5-turbo-16k",
                            "stream": False,
                        },
                    },
                    "json": {
                        "type": "StructureTaskMemoryExtractionEngineJsonConfig",
                        "prompt_driver": {
                            "type": "OpenAiChatPromptDriver",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "model": "gpt-3.5-turbo-16k",
                            "stream": False,
                        },
                    },
                },
                "summary_engine": {
                    "type": "StructureTaskMemorySummaryEngineConfig",
                    "prompt_driver": {
                        "type": "OpenAiChatPromptDriver",
                        "temperature": 0.1,
                        "max_tokens": None,
                        "model": "gpt-3.5-turbo-16k",
                        "stream": False,
                    },
                },
            },
        }

        config = BaseStructureConfig.from_dict(result)

        assert config.to_dict() == OpenAiStructureConfig().to_dict()
