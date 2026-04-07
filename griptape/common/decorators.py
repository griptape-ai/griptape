from __future__ import annotations

import functools
from typing import Any, Callable, Optional, TypeVar, cast, overload

import wrapt
from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


@overload
def observable(wrapped: None = None, **dkwargs: Any) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


@overload
def observable(wrapped: Callable[P, T], **dkwargs: Any) -> Callable[P, T]: ...


def observable(wrapped: Optional[Callable[P, T] | Any] = None, **dkwargs: Any) -> Any:
    if wrapped is None:
        return functools.partial(observable, **dkwargs)

    if not callable(wrapped):
        raise ValueError("Non-callable positional argument passed. Use kwargs to pass arguments to the decorator.")

    @wrapt.decorator
    def wrapper(wrapped: Callable[P, T], instance: Any, args: Any, kwargs: Any) -> T:
        from griptape.common.observable import Observable
        from griptape.observability.observability import Observability

        return cast(
            "T",
            Observability.observe(
                Observable.Call(
                    func=wrapped,
                    instance=instance,
                    args=args,
                    kwargs=kwargs,
                    decorator_args=(),
                    decorator_kwargs=dkwargs,
                )
            ),
        )

    return wrapper(wrapped)  # pyright: ignore[reportCallIssue]
