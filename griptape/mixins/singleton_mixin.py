from __future__ import annotations

import threading

lock = threading.Lock()


class SingletonMixin:
    _instances = {}

    def __new__(cls, *args, **kwargs) -> SingletonMixin:
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(cls, *args, **kwargs)
        return cls._instances[cls]
