from abc import ABC, abstractmethod
from attrs import define
from griptape.common import Observable
from types import TracebackType
from typing import Any, Optional


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
    def observe(self, call: Observable.Call) -> Any: ...
