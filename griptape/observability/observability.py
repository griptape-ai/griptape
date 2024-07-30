from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.common import Observable
from griptape.drivers import BaseObservabilityDriver, NoOpObservabilityDriver

_no_op_observability_driver = NoOpObservabilityDriver()
_global_observability_driver: Optional[BaseObservabilityDriver] = None

if TYPE_CHECKING:
    from types import TracebackType

    from griptape.common import Observable


@define
class Observability:
    observability_driver: BaseObservabilityDriver = field(kw_only=True)

    @staticmethod
    def get_global_driver() -> Optional[BaseObservabilityDriver]:
        global _global_observability_driver
        return _global_observability_driver

    @staticmethod
    def set_global_driver(driver: Optional[BaseObservabilityDriver]) -> None:
        global _global_observability_driver
        _global_observability_driver = driver

    @staticmethod
    def observe(call: Observable.Call) -> Any:
        driver = Observability.get_global_driver() or _no_op_observability_driver
        return driver.observe(call)

    @staticmethod
    def get_span_id() -> Optional[str]:
        driver = Observability.get_global_driver() or _no_op_observability_driver
        return driver.get_span_id()

    def __enter__(self) -> None:
        if Observability.get_global_driver() is not None:
            raise ValueError("Observability driver already set.")
        Observability.set_global_driver(self.observability_driver)
        self.observability_driver.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        Observability.set_global_driver(None)
        self.observability_driver.__exit__(exc_type, exc_value, exc_traceback)
        return False
