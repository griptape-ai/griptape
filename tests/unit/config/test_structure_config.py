from pytest import fixture
from griptape.config import StructureConfig


class TestStructureConfig:
    @fixture
    def config(self):
        return StructureConfig()

    def test_to_dict(self, config):
        assert config.to_dict() == {
            "type": "StructureConfig",
            "global_drivers": {
                "type": "StructureGlobalDriversConfig",
                "prompt_driver": {"type": "DummyPromptDriver", "temperature": 0.1, "max_tokens": None, "stream": False},
                "conversation_memory_driver": None,
                "embedding_driver": {"type": "DummyEmbeddingDriver"},
                "image_generation_driver": {"type": "DummyImageGenerationDriver"},
                "image_query_driver": {"type": "DummyImageQueryDriver"},
                "vector_store_driver": {
                    "embedding_driver": {"type": "DummyEmbeddingDriver"},
                    "type": "DummyVectorStoreDriver",
                },
            },
            "task_memory": {
                "type": "StructureTaskMemoryConfig",
                "query_engine": {
                    "type": "StructureTaskMemoryQueryEngineConfig",
                    "prompt_driver": {
                        "type": "DummyPromptDriver",
                        "stream": False,
                        "temperature": 0.1,
                        "max_tokens": None,
                    },
                    "vector_store_driver": {
                        "type": "DummyVectorStoreDriver",
                        "embedding_driver": {"type": "DummyEmbeddingDriver"},
                    },
                },
                "extraction_engine": {
                    "type": "StructureTaskMemoryExtractionEngineConfig",
                    "csv": {
                        "type": "StructureTaskMemoryExtractionEngineCsvConfig",
                        "prompt_driver": {
                            "type": "DummyPromptDriver",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "stream": False,
                        },
                    },
                    "json": {
                        "type": "StructureTaskMemoryExtractionEngineJsonConfig",
                        "prompt_driver": {
                            "type": "DummyPromptDriver",
                            "temperature": 0.1,
                            "max_tokens": None,
                            "stream": False,
                        },
                    },
                },
                "summary_engine": {
                    "type": "StructureTaskMemorySummaryEngineConfig",
                    "prompt_driver": {
                        "type": "DummyPromptDriver",
                        "temperature": 0.1,
                        "max_tokens": None,
                        "stream": False,
                    },
                },
            },
        }

    def test_from_dict(self, config):
        assert StructureConfig.from_dict(config.to_dict()).to_dict() == config.to_dict()

    def test_unchanged_merge_config(self, config):
        assert (
            config.merge_config(
                {
                    "type": "StructureConfig",
                    "task_memory": {
                        "extraction_engine": {
                            "type": "StructureTaskMemoryExtractionEngineConfig",
                            "csv": {
                                "type": "StructureTaskMemoryExtractionEngineCsvConfig",
                                "prompt_driver": {
                                    "type": "DummyPromptDriver",
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

    def test_dot_update(self, config):
        config.task_memory.extraction_engine.csv.prompt_driver.stream = True

        assert config.task_memory.extraction_engine.csv.prompt_driver.stream is True
