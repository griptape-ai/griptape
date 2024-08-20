from __future__ import annotations


class SingletonMixin:
    _instance = None

    def __new__(cls, *args, **kwargs) -> SingletonMixin:
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)  # noqa: UP008
        return cls._instance
