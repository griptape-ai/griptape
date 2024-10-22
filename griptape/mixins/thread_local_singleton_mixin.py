from __future__ import annotations

import threading

thread_local = threading.local()


class ThreadLocalSingletonMixin:
    def __new__(cls, *args, **kwargs) -> ThreadLocalSingletonMixin:
        if not hasattr(thread_local, "singleton"):
            thread_local.singleton = super().__new__(cls, *args, **kwargs)

        return thread_local.singleton
