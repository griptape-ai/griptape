"""Generic lazy loading utilities for Griptape modules."""

from __future__ import annotations

import importlib
import importlib.util
import pkgutil
from typing import Optional

# Driver-specific mapping: class suffix -> driver type directory
DRIVER_TYPE_SUFFIXES = {
    "PromptDriver": "prompt",
    "ChatPromptDriver": "prompt",
    "EmbeddingDriver": "embedding",
    "VectorStoreDriver": "vector",
    "SqlDriver": "sql",
    "ImageGenerationDriver": "image_generation",
    "ImageGenerationModelDriver": "image_generation_model",
    "ImageGenerationPipelineDriver": "image_generation_pipeline",
    "DiffusionImageGenerationPipelineDriver": "image_generation_pipeline",
    "WebScraperDriver": "web_scraper",
    "WebSearchDriver": "web_search",
    "EventListenerDriver": "event_listener",
    "FileManagerDriver": "file_manager",
    "RerankDriver": "rerank",
    "RulesetDriver": "ruleset",
    "TextToSpeechDriver": "text_to_speech",
    "StructureRunDriver": "structure_run",
    "AudioTranscriptionDriver": "audio_transcription",
    "ObservabilityDriver": "observability",
    "AssistantDriver": "assistant",
    "ConversationMemoryDriver": "memory.conversation",
}


def find_class_module(module_base_path: str, class_name: str, file_suffix: str = "") -> Optional[str]:
    """Find the module containing a class by searching the module directory.

    This uses pkgutil to walk the directory tree and find where the class is actually defined,
    avoiding the need to guess naming conventions.

    Args:
        module_base_path: Base module path to search (e.g., "griptape.structures")
        class_name: The class name to find (e.g., "Agent")
        file_suffix: Optional file suffix to filter by (e.g., "_task", "_tool")

    Returns:
        The full module path if found, None otherwise
    """
    try:
        base_module = importlib.import_module(module_base_path)
        if base_module.__file__ is None:
            return None
        base_dir = str(base_module.__file__).rsplit("/", 1)[0]

        # Walk through all modules in this directory
        for module_info in pkgutil.walk_packages([base_dir], prefix=f"{module_base_path}."):
            # Skip if looking for specific suffix and module doesn't match
            if file_suffix and not module_info.name.endswith(file_suffix):
                continue

            # Try to import and check if it has our class
            try:
                spec = importlib.util.find_spec(module_info.name)
                if spec is not None:
                    module = importlib.import_module(module_info.name)
                    if hasattr(module, class_name):
                        return module_info.name
            except (ImportError, AttributeError):
                continue

    except Exception:
        pass

    return None


def find_driver_module(class_name: str) -> Optional[str]:
    """Find the module containing a driver class by searching the driver directory.

    This is a specialized version of find_class_module for drivers, which uses the
    DRIVER_TYPE_SUFFIXES mapping to narrow the search to the appropriate driver type subdirectory.

    Args:
        class_name: The driver class name to find

    Returns:
        The full module path if found, None otherwise
    """
    # Determine driver type directory from class name suffix
    driver_type = None
    for suffix, dtype in DRIVER_TYPE_SUFFIXES.items():
        if class_name.endswith(suffix):
            driver_type = dtype
            break

    if not driver_type:
        return None

    # Search within the specific driver type directory
    driver_type_path = f"griptape.drivers.{driver_type}"

    try:
        driver_type_module = importlib.import_module(driver_type_path)
        if driver_type_module.__file__ is None:
            return None
        driver_type_dir = str(driver_type_module.__file__).rsplit("/", 1)[0]

        # Walk through all modules in this driver type directory
        for module_info in pkgutil.walk_packages([driver_type_dir], prefix=f"{driver_type_path}."):
            try:
                spec = importlib.util.find_spec(module_info.name)
                if spec is not None:
                    module = importlib.import_module(module_info.name)
                    if hasattr(module, class_name):
                        return module_info.name
            except (ImportError, AttributeError):
                continue

    except Exception:
        pass

    return None
