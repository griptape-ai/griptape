from __future__ import annotations

import threading
from abc import ABC
from concurrent import futures
from typing import Callable, Optional

from attrs import Factory, define, field


@define(slots=False)
class FuturesExecutorMixin(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
        kw_only=True,
    )

    _futures_executor: Optional[futures.Executor] = field(init=False, default=None)
    thread_lock: threading.Lock = field(default=Factory(lambda: threading.Lock()))

    @property
    def futures_executor(self) -> futures.Executor:
        with self.thread_lock:
            if self._futures_executor is None:
                self._futures_executor = self.futures_executor_fn()

        return self._futures_executor

    def __del__(self) -> None:
        with self.thread_lock:
            if self._futures_executor:
                self._futures_executor.shutdown(wait=True)
                self._futures_executor = None
