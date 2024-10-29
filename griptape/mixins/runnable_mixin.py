from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from attrs import define, field

# Generics magic that allows us to reference the type of the class that is implementing the mixin
T = TypeVar("T", bound="RunnableMixin")


@define()
class RunnableMixin(ABC, Generic[T]):
    """Mixin for classes that can be "run".

    Implementing classes should pass themselves as the generic type to ensure that the correct type is used in the callbacks.

    Attributes:
        on_before_run: Optional callback that is called at the very beginning of the `run` method.
        on_after_run: Optional callback that is called at the very end of the `run` method.
    """

    on_before_run: Optional[Callable[[T], None]] = field(kw_only=True, default=None)
    on_after_run: Optional[Callable[[T], None]] = field(kw_only=True, default=None)

    def before_run(self, *args, **kwargs) -> Any:
        if self.on_before_run is not None:
            self.on_before_run(cast(T, self))

    @abstractmethod
    def run(self, *args, **kwargs) -> Any: ...

    def after_run(self, *args, **kwargs) -> Any:
        if self.on_after_run is not None:
            self.on_after_run(cast(T, self))
