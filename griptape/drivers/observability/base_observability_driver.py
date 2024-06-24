from abc import ABC, abstractmethod
from types import TracebackType
from attrs import define
from typing import Any, Callable, Optional


@define
class BaseObservabilityDriver(ABC):
    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        return False

    @abstractmethod
    def invoke_observable(
        self,
        func: Callable,
        instance: Optional[Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        decorator_args: tuple[Any, ...],
        decorator_kwargs: dict[str, Any],
    ) -> Any: ...
