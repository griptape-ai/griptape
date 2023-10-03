import sys
from types import ModuleType
import json
import importlib
from typing import Any, Literal, Optional
from .j2 import J2
from .conversation import Conversation
from .manifest_validator import ManifestValidator
from .python_runner import PythonRunner
from .command_runner import CommandRunner
from .chat import Chat
from .futures import execute_futures_dict
from .token_counter import TokenCounter
from .prompt_stack import PromptStack
from .dict_utils import remove_null_values_in_dict_recursively
from .hash import str_to_hash


def minify_json(value: str) -> str:
    return json.dumps(json.loads(value), separators=(",", ":"))


def lazy_load(module_name: str, package_name: str, element: str) -> Any:
    def f(*args: Any, **kwargs: Any) -> Any:
        try:
            module = importlib.import_module(module_name, package_name)
            e = getattr(module, element)(*args, **kwargs)
            return e
        except ImportError: 
            raise ImportError(f"Lazy load failed for {module_name}.{element}")

    setattr(f, "name", module_name.replace(".", ""))
    setattr(f, "package", package_name)
    setattr(f, "element", element)
    return f

INSTALL_MAPPING = {}

def import_optional_dependency(
    name: str,
    extra: str,
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
        f"Use poetry or pip to install the extra: {extra}."
    )
    try:
        module = importlib.import_module(name)
    except ImportError:
        if errors == "raise":
            raise ImportError(msg)
        else:
            return None

    # Handle submodules: if we have submodule, grab parent module from sys.modules
    parent = name.split(".")[0]
    if parent != name:
        install_name = parent
        module_to_get = sys.modules[install_name]
    else:
        module_to_get = module
    return module_to_get


__all__ = [
    "Conversation",
    "ManifestValidator",
    "PythonRunner",
    "CommandRunner",
    "minify_json",
    "J2",
    "Chat",
    "str_to_hash",
    "lazy_load",
    "import_optional_dependency",
    "execute_futures_dict",
    "TokenCounter",
    "PromptStack",
    "remove_null_values_in_dict_recursively",
]
