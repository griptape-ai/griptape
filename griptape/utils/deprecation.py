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
        if name not in self.__ignore_attrs__:
            warnings.warn(
                self._deprecation_message,
                DeprecationWarning,
                stacklevel=2,
            )
        return getattr(self._real_module, name)


def deprecation_warn(message: str, stacklevel: int = 2) -> None:
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning, stacklevel=stacklevel)
    warnings.simplefilter("default", DeprecationWarning)
