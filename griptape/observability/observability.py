from types import TracebackType
from typing import Any, Callable, Optional
from attrs import define, field
from griptape.drivers.observability.base_observability_driver import BaseObservabilityDriver
from griptape.drivers.observability.no_op_observability_driver import NoOpObservabilityDriver

_no_op_observability_driver = NoOpObservabilityDriver()
_global_observability_driver: Optional[BaseObservabilityDriver] = None


@define
class Observability:
    observability_driver: BaseObservabilityDriver = field(kw_only=True)

    @staticmethod
    def get_global_driver() -> Optional[BaseObservabilityDriver]:
        global _global_observability_driver
        return _global_observability_driver

    @staticmethod
    def set_global_driver(driver: Optional[BaseObservabilityDriver]):
        global _global_observability_driver
        _global_observability_driver = driver

    @staticmethod
    def invoke_observable(
        func: Callable,
        instance: Optional[Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        decorator_args: tuple[Any, ...],
        decorator_kwargs: dict[str, Any],
    ) -> Any:
        driver = Observability.get_global_driver() or _no_op_observability_driver
        return driver.invoke_observable(func, instance, args, kwargs, decorator_args, decorator_kwargs)

    def __enter__(self):
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
