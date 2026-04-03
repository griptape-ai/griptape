import contextvars
from collections.abc import Callable
from typing import Any


def with_contextvars(wrapped: Callable) -> Callable:
    ctx = contextvars.copy_context()

    def wrapper(*args, **kwargs) -> Any:
        return ctx.run(wrapped, *args, **kwargs)

    return wrapper
