from __future__ import annotations

import logging
import threading

thread_local = threading.local()


class ThreadLocalSingletonMixin:
    def __new__(cls, *args, **kwargs) -> ThreadLocalSingletonMixin:
        if not hasattr(thread_local, "singleton"):
            logging.getLogger(__name__).info(f"Creating new singleton instance of {cls.__name__}")
            thread_local.singleton = super().__new__(cls, *args, **kwargs)
        else:
            logging.getLogger(__name__).info(f"Reusing existing singleton instance of {cls.__name__}")

        return thread_local.singleton
