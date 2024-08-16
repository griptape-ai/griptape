from __future__ import annotations

from abc import ABC
from concurrent import futures
from threading import Lock
from typing import Callable, Optional

from attrs import Factory, define, field


@define(slots=False)
class FuturesExecutorMixin(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
        kw_only=True,
    )

    _futures_executor: Optional[futures.Executor] = field(init=False, default=None)
    _executor_lock: Lock = field(init=False, factory=Lock)

    @property
    def futures_executor(self) -> futures.Executor:
        if self._futures_executor is None:
            with self._executor_lock:
                if self._futures_executor is None:
                    self._futures_executor = self.futures_executor_fn()

        return self._futures_executor

    def __del__(self) -> None:
        with self._executor_lock:
            if self._futures_executor:
                self._futures_executor.shutdown(True)
                self._futures_executor = None
