from importlib import import_module
from types import ModuleType
from typing import Literal, Optional


INSTALL_MAPPING = {}

def import_optional_dependency(
    name: str,
    errors: Literal["raise", "ignore"] = "raise",
) -> Optional[ModuleType]:
    """Import an optional dependency.

    By default, if a dependency is missing an ImportError with a nice
    message will be raised.

    Args:
        name: The module name.
        extra: Additional text to include in the ImportError message.
        errors: What to do when a dependency is not found
                * raise : Raise an ImportError
                * ignore: If the module is not installed, return None.
    Returns:
        The imported module, when found.
        None is returned when the package is not found and `errors` is False.
    """

    assert errors in {"warn", "raise", "ignore"}

    package_name = INSTALL_MAPPING.get(name)
    install_name = package_name if package_name is not None else name

    msg = (
        f"Missing optional dependency: '{install_name}'. "
        f"Use poetry or pip to install the required extra."
    )
    try:
        module = import_module(name)
    except ImportError:
        if errors == "raise":
            raise ImportError(msg)
        else:
            return None

    return module

