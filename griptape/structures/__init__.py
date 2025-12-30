# Lazy loading mapping: maps class names to their import paths
_STRUCTURE_IMPORTS = {
    "Structure": ("griptape.structures.structure", "Structure"),
    "Agent": ("griptape.structures.agent", "Agent"),
    "Pipeline": ("griptape.structures.pipeline", "Pipeline"),
    "Workflow": ("griptape.structures.workflow", "Workflow"),
}


def __getattr__(name: str):
    """Lazily import structures only when accessed."""
    if name in _STRUCTURE_IMPORTS:
        module_path, class_name = _STRUCTURE_IMPORTS[name]
        from importlib import import_module

        module = import_module(module_path)
        structure_class = getattr(module, class_name)
        # Cache the imported class in the module's namespace
        globals()[name] = structure_class
        return structure_class
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Support for dir() and tab completion."""
    return list(_STRUCTURE_IMPORTS.keys())


__all__ = ["Agent", "Pipeline", "Structure", "Workflow"]
