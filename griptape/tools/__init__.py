import importlib
from typing import Any

from griptape.common._lazy_loader import find_class_module


def __getattr__(name: str) -> Any:
    """Lazy-load tool classes on first access.

    Args:
        name: The name of the tool class to import

    Returns:
        The tool class

    Raises:
        AttributeError: If the tool class cannot be found
    """
    # Find the module containing this tool
    module_path = find_class_module("griptape.tools", name)

    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Import and cache the tool
    try:
        module = importlib.import_module(module_path)
        tool_class = getattr(module, name)
        # Cache for future access
        globals()[name] = tool_class
        return tool_class
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from e


def __dir__() -> list[str]:
    """Support dir() and IDE autocomplete.

    Returns:
        List of all available tool names (from __all__)
    """
    # Return __all__ which contains the complete list
    return __all__


__all__ = [  # pyright: ignore[reportUnsupportedDunderAll]
    "AudioTranscriptionTool",
    "BaseTool",
    "BaseImageGenerationTool",
    "CalculatorTool",
    "ComputerTool",
    "DateTimeTool",
    "EmailTool",
    "ExtractionTool",
    "FileManagerTool",
    "GriptapeCloudToolTool",
    "ImageQueryTool",
    "InpaintingImageGenerationTool",
    "MCPTool",
    "OutpaintingImageGenerationTool",
    "PromptImageGenerationTool",
    "PromptSummaryTool",
    "QueryTool",
    "RagTool",
    "RestApiTool",
    "SqlTool",
    "StructuredOutputTool",
    "StructureRunTool",
    "TextToSpeechTool",
    "VariationImageGenerationTool",
    "VectorStoreTool",
    "WebScraperTool",
    "WebSearchTool",
]
