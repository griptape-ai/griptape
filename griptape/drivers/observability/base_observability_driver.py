from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from attrs import define

if TYPE_CHECKING:
    from types import TracebackType

    from griptape.common import Observable


@define
class BaseObservabilityDriver(ABC):
    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        return False

    @abstractmethod
    def observe(self, call: Observable.Call) -> Any:
        pass

    @abstractmethod
    def get_span_id(self) -> str | None:
        pass
