from pytest import fixture
from griptape.config import OpenAiStructureConfig


class TestOpenAiStructureConfig:
    @fixture
    def config(self):
        return OpenAiStructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "OpenAiStructureConfig",
            "prompt_driver": {
                "type": "OpenAiChatPromptDriver",
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": None,
                "stream": False,
            },
            "task_memory": {
                "type": "StructureTaskMemoryConfig",
                "query_engine": {
                    "type": "StructureTaskMemoryQueryEngineConfig",
                    "prompt_driver": {
                        "type": "OpenAiChatPromptDriver",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.1,
                        "max_tokens": None,
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
                            "model": "gpt-3.5-turbo",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "stream": False,
                        },
                    },
                    "json": {
                        "type": "StructureTaskMemoryExtractionEngineJsonConfig",
                        "prompt_driver": {
                            "type": "OpenAiChatPromptDriver",
                            "model": "gpt-3.5-turbo",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "stream": False,
                        },
                    },
                },
                "summary_engine": {
                    "type": "StructureTaskMemorySummaryEngineConfig",
                    "prompt_driver": {
                        "type": "OpenAiChatPromptDriver",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.1,
                        "max_tokens": None,
                        "stream": False,
                    },
                },
            },
        }

    def test_from_dict(self, config):
        assert OpenAiStructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_unchanged_merge_config(self, config):
        assert (
            config.merge_config(
                {
                    "type": "OpenAiStructureConfig",
                    "task_memory": {
                        "extraction_engine": {
                            "type": "StructureTaskMemoryExtractionEngineConfig",
                            "csv": {
                                "type": "StructureTaskMemoryExtractionEngineCsvConfig",
                                "prompt_driver": {
                                    "type": "OpenAiChatPromptDriver",
                                    "model": "gpt-3.5-turbo",
                                    "temperature": 0.1,
                                    "max_tokens": None,
                                    "stream": False,
                                },
                            },
                        }
                    },
                }
            ).to_dict()
            == config.to_dict()
        )

    def test_changed_merge_config(self, config):
        config = config.merge_config(
            {"task_memory": {"extraction_engine": {"csv": {"prompt_driver": {"stream": True}}}}}
        )

        assert config.task_memory.extraction_engine.csv.prompt_driver.stream is True
