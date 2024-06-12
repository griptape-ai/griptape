from abc import ABC, abstractmethod
from typing import Any


class BaseObservabilityDriver(ABC):
    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    @abstractmethod
    def invoke_observable(self, func, instance, args, kwargs, decorator_args, decorator_kwargs) -> Any: ...
