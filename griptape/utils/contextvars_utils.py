import contextvars
import threading
from collections.abc import Callable
from typing import Any


def with_contextvars(wrapped: Callable) -> Callable:
    ctx = contextvars.copy_context()
    lock = threading.Lock()

    def wrapper(*args, **kwargs) -> Any:
        with lock:
            ctx_copy = ctx.run(contextvars.copy_context)
        return ctx_copy.run(wrapped, *args, **kwargs)

    return wrapper
