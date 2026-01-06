import importlib
from typing import Any

from griptape.common._lazy_loader import find_class_module, discover_all_classes


def __getattr__(name: str) -> Any:
    """Lazy-load task classes on first access.

    Args:
        name: The name of the task class to import

    Returns:
        The task class

    Raises:
        AttributeError: If the task class cannot be found
    """
    # Find the module containing this task
    module_path = find_class_module("griptape.tasks", name)

    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Import and cache the task
    try:
        module = importlib.import_module(module_path)
        task_class = getattr(module, name)
        # Cache for future access
        globals()[name] = task_class
        return task_class
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from e


def __dir__() -> list[str]:
    """Support dir() and IDE autocomplete.

    Returns:
        List of all available task names
    """
    base_names = [name for name in globals() if not name.startswith("_")]
    discovered = discover_all_classes("griptape.tasks")
    return sorted(set(base_names + discovered))


__all__ = [
    "ActionsSubtask",
    "OutputSchemaValidationSubtask",
    "AssistantTask",
    "AudioTranscriptionTask",
    "BaseAudioGenerationTask",
    "BaseImageGenerationTask",
    "BaseTask",
    "BaseSubtask",
    "BaseTextInputTask",
    "BranchTask",
    "CodeExecutionTask",
    "ExtractionTask",
    "InpaintingImageGenerationTask",
    "OutpaintingImageGenerationTask",
    "PromptImageGenerationTask",
    "PromptTask",
    "RagTask",
    "StructureRunTask",
    "TextSummaryTask",
    "TextToSpeechTask",
    "ToolTask",
    "ToolkitTask",
    "VariationImageGenerationTask",
]
