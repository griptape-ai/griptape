import sys
import warnings
from types import ModuleType
from typing import Any


class DeprecationModuleWrapper(ModuleType):
    """Module wrapper that issues a deprecation warning when importing."""

    __ignore_attrs__ = {
        "__file__",
        "__package__",
        "__path__",
        "__doc__",
        "__all__",
        "__name__",
        "__loader__",
        "__spec__",
    }

    def __init__(self, real_module: Any, deprecation_message: str) -> None:
        self._real_module = real_module
        self._deprecation_message = deprecation_message

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._real_module, name)
        if name not in self.__ignore_attrs__:
            package = self._replacement_package(name, value)
            replacement = f" Use `from {package} import {name}` instead." if package else ""
            warnings.warn(
                f"{self._deprecation_message.strip()}{replacement}",
                DeprecationWarning,
                stacklevel=2,
            )
        return value

    def _replacement_package(self, name: str, value: Any) -> str | None:
        """Return the package that re-exports `name`, or None if it cannot be determined.

        `value.__module__` is the module the symbol is *defined* in, which for this
        codebase is a private implementation module (`...prompt.openai_chat_prompt_driver`).
        The documented import path is the package that re-exports it
        (`...prompt.openai`), so look for that package among the already-imported
        subpackages of the defining module's parent, preferring the most specific one.
        """
        defining_module = getattr(value, "__module__", None)
        if not isinstance(defining_module, str) or not defining_module:
            return None

        parent_name = defining_module.rpartition(".")[0]
        parent = sys.modules.get(parent_name)
        if parent is None or parent is self or parent is self._real_module:
            return None

        candidates = [parent_name] if getattr(parent, name, None) is value else []
        candidates += [
            module.__name__
            for module in list(vars(parent).values())
            if isinstance(module, ModuleType)
            and not isinstance(module, DeprecationModuleWrapper)
            and hasattr(module, "__path__")
            and getattr(module, name, None) is value
        ]

        return max(candidates, key=lambda candidate: candidate.count("."), default=None)


def deprecation_warn(message: str, stacklevel: int = 2) -> None:
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)
    warnings.simplefilter("default", DeprecationWarning)
