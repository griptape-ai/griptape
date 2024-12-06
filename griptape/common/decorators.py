from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

import wrapt

T = TypeVar("T")


def observable(*dargs: Any, **dkwargs: Any) -> Callable:
    @wrapt.decorator
    def decorator(wrapped: Callable[..., T], instance: Any, args: Any, kwargs: Any) -> T:
        from griptape.common.observable import Observable
        from griptape.observability.observability import Observability

        return cast(
            T,
            Observability.observe(
                Observable.Call(
                    func=wrapped,
                    instance=instance,
                    args=args,
                    kwargs=kwargs,
                    decorator_args=dargs,
                    decorator_kwargs=dkwargs,
                )
            ),
        )

    # Check if it's being called as @observable or @observable(...)
    if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:  # pyright: ignore[reportArgumentType]
        # Case when decorator is used without arguments
        func = dargs[0]
        dargs = ()
        dkwargs = {}
        return decorator(func)  # pyright: ignore[reportCallIssue]
    else:
        # Case when decorator is used with arguments
        return decorator
