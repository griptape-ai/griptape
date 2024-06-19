from typing import Any, Callable, Optional
from griptape.drivers.observability.base_observability_driver import BaseObservabilityDriver


class NoOpObservabilityDriver(BaseObservabilityDriver):
    def invoke_observable(
        self,
        func: Callable,
        instance: Optional[Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        decorator_args: tuple[Any, ...],
        decorator_kwargs: dict[str, Any],
    ) -> Any:
        return func(*args, **kwargs)
