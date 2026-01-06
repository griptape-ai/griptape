"""Tests for the lazy loading utilities in griptape.common._lazy_loader."""

import pytest

from griptape.common._lazy_loader import (
    DRIVER_TYPE_SUFFIXES,
    find_class_module,
    find_driver_module,
)


class TestLazyLoader:
    """Test suite for lazy loading utilities."""

    def test_find_class_module_structures(self):
        """Test finding structure classes."""
        # Test finding Agent
        result = find_class_module("griptape.structures", "Agent")
        assert result == "griptape.structures.agent"

        # Test finding Pipeline
        result = find_class_module("griptape.structures", "Pipeline")
        assert result == "griptape.structures.pipeline"

        # Test non-existent class
        result = find_class_module("griptape.structures", "NonExistentStructure")
        assert result is None

    def test_find_class_module_tasks(self):
        """Test finding task classes."""
        # Test finding PromptTask
        result = find_class_module("griptape.tasks", "PromptTask")
        assert result == "griptape.tasks.prompt_task"

        # Test finding ToolTask
        result = find_class_module("griptape.tasks", "ToolTask")
        assert result == "griptape.tasks.tool_task"

        # Test non-existent task
        result = find_class_module("griptape.tasks", "NonExistentTask")
        assert result is None

    def test_find_class_module_tools(self):
        """Test finding tool classes."""
        # Test finding WebScraperTool
        result = find_class_module("griptape.tools", "WebScraperTool")
        assert result is not None
        assert "web_scraper" in result

        # Test finding CalculatorTool
        result = find_class_module("griptape.tools", "CalculatorTool")
        assert result is not None
        assert "calculator" in result

        # Test non-existent tool
        result = find_class_module("griptape.tools", "NonExistentTool")
        assert result is None

    def test_find_driver_module_prompt_drivers(self):
        """Test finding prompt driver classes."""
        # Test OpenAI prompt driver - should find it somewhere in prompt drivers
        result = find_driver_module("OpenAiChatPromptDriver")
        assert result is not None
        assert "griptape.drivers.prompt" in result
        assert "openai" in result.lower()

        # Test Anthropic prompt driver
        result = find_driver_module("AnthropicPromptDriver")
        assert result is not None
        assert "griptape.drivers.prompt.anthropic" in result

        # Test Cohere prompt driver
        result = find_driver_module("CoherePromptDriver")
        assert result is not None
        assert "griptape.drivers.prompt.cohere" in result

    def test_find_driver_module_embedding_drivers(self):
        """Test finding embedding driver classes."""
        result = find_driver_module("OpenAiEmbeddingDriver")
        assert result is not None
        assert "griptape.drivers.embedding" in result
        assert "openai" in result.lower()

        result = find_driver_module("CohereEmbeddingDriver")
        assert result is not None
        assert "griptape.drivers.embedding.cohere" in result

    def test_find_driver_module_vector_store_drivers(self):
        """Test finding vector store driver classes."""
        result = find_driver_module("LocalVectorStoreDriver")
        assert result is not None
        assert "griptape.drivers.vector" in result
        assert "local" in result

        result = find_driver_module("PineconeVectorStoreDriver")
        assert result is not None
        assert "griptape.drivers.vector" in result
        assert "pinecone" in result

    def test_find_driver_module_with_subdirectories(self):
        """Test finding drivers in subdirectories (like Azure)."""
        # Azure driver has a subdirectory structure
        result = find_driver_module("AzureOpenAiChatPromptDriver")
        assert result is not None
        assert "azure" in result.lower()

    def test_find_driver_module_with_numbers(self):
        """Test finding drivers with numbers in the name."""
        result = find_driver_module("StableDiffusion3ImageGenerationPipelineDriver")
        assert result is not None
        assert "stable_diffusion" in result

    def test_find_driver_module_non_existent(self):
        """Test finding non-existent driver."""
        result = find_driver_module("NonExistentDriver")
        assert result is None

    def test_find_driver_module_invalid_suffix(self):
        """Test finding driver with invalid suffix (not ending in known suffix)."""
        result = find_driver_module("InvalidSuffix")
        assert result is None

    def test_driver_type_suffixes_coverage(self):
        """Test that all driver type suffixes are defined."""
        expected_suffixes = {
            "PromptDriver",
            "ChatPromptDriver",
            "EmbeddingDriver",
            "VectorStoreDriver",
            "SqlDriver",
            "ImageGenerationDriver",
            "ImageGenerationModelDriver",
            "ImageGenerationPipelineDriver",
            "DiffusionImageGenerationPipelineDriver",
            "WebScraperDriver",
            "WebSearchDriver",
            "EventListenerDriver",
            "FileManagerDriver",
            "RerankDriver",
            "RulesetDriver",
            "TextToSpeechDriver",
            "StructureRunDriver",
            "AudioTranscriptionDriver",
            "ObservabilityDriver",
            "AssistantDriver",
            "ConversationMemoryDriver",
        }
        assert set(DRIVER_TYPE_SUFFIXES.keys()) == expected_suffixes


class TestLazyLoadingIntegration:
    """Integration tests for lazy loading in actual modules."""

    def test_drivers_lazy_loading(self):
        """Test that drivers module uses lazy loading."""
        # Import the drivers module
        from griptape.drivers import DummyPromptDriver

        # Access the driver - this should trigger lazy loading
        driver_class = DummyPromptDriver

        # Verify it's the correct class
        assert driver_class.__name__ == "DummyPromptDriver"

        # Verify the class is functional
        assert hasattr(driver_class, "__init__")

    def test_structures_lazy_loading(self):
        """Test that structures module uses lazy loading."""
        # Import the structures module
        import griptape.structures as structures

        # Access a structure - this should trigger lazy loading
        agent_class = structures.Agent

        # Verify it's cached
        assert "Agent" in structures.__dict__

        # Verify it's the correct class
        assert agent_class.__name__ == "Agent"

    def test_tasks_lazy_loading(self):
        """Test that tasks module uses lazy loading."""
        import griptape.tasks as tasks

        # Access a task - this should trigger lazy loading
        prompt_task_class = tasks.PromptTask

        # Verify it's cached
        assert "PromptTask" in tasks.__dict__

        # Verify it's the correct class
        assert prompt_task_class.__name__ == "PromptTask"

    def test_tools_lazy_loading(self):
        """Test that tools module uses lazy loading."""
        import griptape.tools as tools

        # Access a tool - this should trigger lazy loading
        calculator_tool_class = tools.CalculatorTool

        # Verify it's cached
        assert "CalculatorTool" in tools.__dict__

        # Verify it's the correct class
        assert calculator_tool_class.__name__ == "CalculatorTool"

    def test_driver_lazy_loading_error_handling(self):
        """Test that lazy loading raises appropriate errors for invalid drivers."""
        import griptape.drivers as drivers

        with pytest.raises(AttributeError, match="has no attribute 'NonExistentDriver'"):
            _ = drivers.NonExistentDriver

    def test_structure_lazy_loading_error_handling(self):
        """Test that lazy loading raises appropriate errors for invalid structures."""
        import griptape.structures as structures

        with pytest.raises(AttributeError, match="has no attribute 'NonExistentStructure'"):
            _ = structures.NonExistentStructure

    def test_lazy_loading_caching(self):
        """Test that lazy loading caches imports properly."""
        import griptape.drivers as drivers

        # First access
        driver1 = drivers.DummyPromptDriver
        # Second access - should return cached version
        driver2 = drivers.DummyPromptDriver

        # Should be the exact same object
        assert driver1 is driver2

    def test_dir_includes_all_classes(self):
        """Test that __dir__ returns all classes from __all__."""
        # Import from the actual module path to avoid the deprecation wrapper
        from griptape import drivers

        # Get the real module if it's wrapped
        if hasattr(drivers, "_real_module"):
            drivers = drivers._real_module

        available = dir(drivers)

        # Should include base classes
        assert "BasePromptDriver" in available
        assert "BaseEmbeddingDriver" in available

        # Should include concrete drivers with correct capitalization
        assert "OpenAiChatPromptDriver" in available  # Correct: OpenAi not Openai
        assert "AnthropicPromptDriver" in available
        assert "DummyPromptDriver" in available
        assert "MongoDbAtlasVectorStoreDriver" in available  # Correct: MongoDb not Mongodb

        # Should have 112 concrete drivers + base classes
        driver_count = len([name for name in available if name.endswith("Driver")])
        assert driver_count >= 112

    def test_all_drivers_are_importable(self):
        """Test that all drivers in __all__ can be lazily imported."""
        import griptape.drivers as drivers_module

        # Test a representative sample (testing all 112 would be slow)
        sample_drivers = [
            "OpenAiChatPromptDriver",  # OpenAI with capital AI
            "AzureOpenAiChatPromptDriver",  # Azure variant
            "MongoDbAtlasVectorStoreDriver",  # MongoDB with capital DB
            "AnthropicPromptDriver",
            "LocalVectorStoreDriver",
            "DummyPromptDriver",
            "LocalConversationMemoryDriver",  # Nested directory
        ]

        for driver_name in sample_drivers:
            # Import the driver
            driver_class = getattr(drivers_module, driver_name)
            # Verify it's the correct class
            assert driver_class.__name__ == driver_name
            # Verify it's a class
            assert isinstance(driver_class, type)

    def test_all_exports(self):
        """Test that __all__ is properly defined."""
        import griptape.drivers as drivers
        import griptape.structures as structures
        import griptape.tasks as tasks
        import griptape.tools as tools

        # All modules should have __all__ defined
        assert hasattr(drivers, "__all__")
        assert hasattr(structures, "__all__")
        assert hasattr(tasks, "__all__")
        assert hasattr(tools, "__all__")

        # __all__ should be a list
        assert isinstance(drivers.__all__, list)
        assert isinstance(structures.__all__, list)
        assert isinstance(tasks.__all__, list)
        assert isinstance(tools.__all__, list)

        # Should contain expected items
        assert "BasePromptDriver" in drivers.__all__
        assert "OpenAiChatPromptDriver" in drivers.__all__
        assert "Agent" in structures.__all__
        assert "PromptTask" in tasks.__all__
