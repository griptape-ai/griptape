import importlib
from typing import Any

from griptape.common._lazy_loader import find_class_module


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
        List of all available task names (from __all__)
    """
    # Return __all__ which contains the complete list
    return __all__


__all__ = [  # pyright: ignore[reportUnsupportedDunderAll]
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
