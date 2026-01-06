import importlib
from typing import Any

from griptape.common._lazy_loader import find_class_module, discover_all_classes


def __getattr__(name: str) -> Any:
    """Lazy-load structure classes on first access.

    Args:
        name: The name of the structure class to import

    Returns:
        The structure class

    Raises:
        AttributeError: If the structure class cannot be found
    """
    # Find the module containing this structure
    module_path = find_class_module("griptape.structures", name)

    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Import and cache the structure
    try:
        module = importlib.import_module(module_path)
        structure_class = getattr(module, name)
        # Cache for future access
        globals()[name] = structure_class
        return structure_class
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from e


def __dir__() -> list[str]:
    """Support dir() and IDE autocomplete.

    Returns:
        List of all available structure names
    """
    base_names = [name for name in globals().keys() if not name.startswith("_")]
    discovered = discover_all_classes("griptape.structures")
    return sorted(set(base_names + discovered))


__all__ = ["Agent", "Pipeline", "Structure", "Workflow"]
