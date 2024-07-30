from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from attrs import define

if TYPE_CHECKING:
    from types import TracebackType

    from griptape.common import Observable


@define
class BaseObservabilityDriver(ABC):
    def __enter__(self) -> None:  # noqa: B027
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

    @abstractmethod
    def get_span_id(self) -> Optional[str]: ...
