import contextvars
from typing import Any, Callable


def with_contextvars(wrapped: Callable) -> Callable:
    ctx = contextvars.copy_context()

    def wrapper(*args, **kwargs) -> Any:
        return ctx.run(wrapped, *args, **kwargs)

    return wrapper
