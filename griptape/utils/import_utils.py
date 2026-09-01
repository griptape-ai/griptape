from __future__ import annotations

import logging
from functools import cache
from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

# Child of the "griptape" logger. Naming it via `Defaults` would cycle: configs imports utils.
logger = logging.getLogger(__name__)

INSTALL_MAPPING = {
    "huggingface_hub": "huggingface-hub",
    "pinecone": "pinecone-client",
    "opensearchpy": "opensearch-py",
    "google.genai": "google-genai",
}


def import_optional_dependency(name: str) -> ModuleType:
    """Import an optional dependency.

    If a dependency is missing, an ImportError with a nice message will be raised.

    Args:
        name: The module name.

    Returns:
        The imported module, when found.
    """
    package_name = INSTALL_MAPPING.get(name)
    install_name = package_name if package_name is not None else name

    msg = (
        f"Missing optional dependency: '{install_name}'. "
        f"Please install the appropriate extra: https://docs.griptape.ai/stable/griptape-framework/#extras."
    )
    try:
        module = import_module(name)
    except ImportError as exc:
        raise ImportError(msg) from exc

    return module


def is_dependency_installed(name: str) -> bool:
    """Check if an optional dependency is available.

    Args:
        name: The module name.

    Returns:
        True if the dependency is available.
        False if the dependency is not available.
    """
    try:
        import_optional_dependency(name)
    except ImportError:
        return False

    return True


@cache
def optional_type(name: str, attr: str | None = None) -> Any:
    """Resolve an optional dependency's module or attribute for an annotation, or `Any`.

    An unimportable dependency must not raise, or it fails serialization of objects that never
    touch it, so it degrades to `Any` -- silently when merely absent, with a warning when
    installed and broken. A missing attribute on a real module still raises `AttributeError`,
    since a wrong name or upstream rename is a bug and `Any` would hide it. Cached per name, so a
    broken dependency is reported once rather than on every `to_dict()`.

    `Any` only satisfies a name used BARE in an annotation. `boto3` and `openai` are annotated
    dotted (`boto3.Session`), so those entries degrade to `Any.Session` and fail; fixing that
    needs a shim, not a fallback value.

    Args:
        name: The module name.
        attr: An attribute to resolve on the module. None returns the module itself.

    Returns:
        The module or attribute, or `Any` when the dependency is absent or unimportable.
    """
    try:
        module = import_module(name)
    except ImportError as exc:
        if _is_absent(name, exc):
            return Any
        return _warn_unimportable(name, attr, exc)

    if attr is None:
        return module

    try:
        return getattr(module, attr)
    except ImportError as exc:
        return _warn_unimportable(name, attr, exc)
    except AttributeError as exc:
        # An empty directory on sys.path imports as a namespace package: a package (`__path__`)
        # with no module of its own (`__file__`), so every attribute is missing. That is a broken
        # environment, not a wrong name.
        if hasattr(module, "__path__") and getattr(module, "__file__", None) is None:
            return _warn_unimportable(name, attr, exc)
        raise


def _warn_unimportable(name: str, attr: str | None, exc: Exception) -> Any:
    """Report an installed-but-unusable dependency and fall back to `Any`."""
    logger.warning(
        "Optional dependency '%s' is installed but could not be imported, so it is treated as "
        "`Any`. This usually means a broken install, or a conflicting version of one of its own "
        "dependencies. Underlying error: %s",
        name if attr is None else f"{name}.{attr}",
        exc,
    )
    return Any


def _is_absent(name: str, exc: ImportError) -> bool:
    """Whether the dependency is not installed, as opposed to installed and broken.

    Both raise from the same hierarchy, so the requested module is compared against the missing one.
    """
    if not isinstance(exc, ModuleNotFoundError) or exc.name is None:
        return False
    return name == exc.name or name.startswith(f"{exc.name}.")
