from __future__ import annotations

import functools
from inspect import isfunction
from typing import Any, Callable, Optional, TypeVar, cast

from attrs import Factory, define, field

T = TypeVar("T", bound=Callable)


def observable(*args: T | Any, **kwargs: Any) -> T:
    return cast(T, Observable(*args, **kwargs))


class Observable:
    @define
    class Call:
        func: Callable = field(kw_only=True)
        instance: Optional[Any] = field(default=None, kw_only=True)
        args: tuple[Any, ...] = field(default=Factory(tuple), kw_only=True)
        kwargs: dict[str, Any] = field(default=Factory(dict), kw_only=True)
        decorator_args: tuple[Any, ...] = field(default=Factory(tuple), kw_only=True)
        decorator_kwargs: dict[str, Any] = field(default=Factory(dict), kw_only=True)

        def __call__(self) -> Any:
            # If self.func has a __self__ attribute, it is a bound method and we do not need to pass the instance.
            args = (self.instance, *self.args) if self.instance and not hasattr(self.func, "__self__") else self.args
            return self.func(*args, **self.kwargs)

        @property
        def tags(self) -> Optional[list[str]]:
            return self.decorator_kwargs.get("tags")

    def __init__(self, *args, **kwargs) -> None:
        self._instance = None
        if len(args) == 1 and len(kwargs) == 0 and isfunction(args[0]):
            # Parameterless call. In otherwords, the `@observable` annotation
            # was not followed by parentheses.
            self._func = args[0]
            functools.update_wrapper(self, self._func)
            self.decorator_args = ()
            self.decorator_kwargs = {}
        else:
            # Parameterized call. In otherwords, the `@observable` annotation
            # was followed by parentheses, for example `@observable()`,
            # `@observable("x")` or `@observable(y="y")`.
            self._func = None
            self.decorator_args = args
            self.decorator_kwargs = kwargs

    def __get__(self, obj: Any, objtype: Any = None) -> Observable:
        self._instance = obj
        return self

    def __call__(self, *args, **kwargs) -> Any:
        if self._func:
            # Parameterless call (self._func was a set in __init__)
            from griptape.observability.observability import Observability

            return Observability.observe(
                Observable.Call(
                    func=self._func,
                    instance=self._instance,
                    args=args,
                    kwargs=kwargs,
                    decorator_args=self.decorator_args,
                    decorator_kwargs=self.decorator_kwargs,
                )
            )
        else:
            # Parameterized call, create and return the "real" observable decorator
            func = args[0]
            decorated_func = Observable(func)
            decorated_func.decorator_args = self.decorator_args
            decorated_func.decorator_kwargs = self.decorator_kwargs
            return decorated_func
