from __future__ import annotations

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

    @property
    def futures_executor(self) -> futures.Executor:
        if self._futures_executor is None:
            self._futures_executor = self.futures_executor_fn()

        return self._futures_executor

    def __del__(self) -> None:
        if self._futures_executor:
            self._futures_executor.shutdown()
            self._futures_executor = None
