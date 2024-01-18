from griptape.config import OpenAiStructureConfig


class TestOpenAiStructureConfig:
    def test_to_dict(self):
        openai_structure_config = OpenAiStructureConfig()

        print(openai_structure_config.to_json())
        assert openai_structure_config.to_dict() == {
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

    def test_from_dict(self):
        openai_structure_config = OpenAiStructureConfig()

        assert (
            OpenAiStructureConfig.from_dict(openai_structure_config.to_dict()).to_dict()
            == openai_structure_config.to_dict()
        )
