import contextvars
import functools
from typing import Callable


def with_contextvars(wrapped: Callable) -> Callable:
    ctx = contextvars.copy_context()

    return functools.partial(ctx.run, wrapped)
