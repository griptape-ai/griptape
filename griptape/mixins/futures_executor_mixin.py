from __future__ import annotations

from abc import ABC
from concurrent import futures
from typing import Callable, Optional

from attrs import Factory, define, field


@define(slots=False, kw_only=True)
class FuturesExecutorMixin(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
    )

    futures_executor: Optional[futures.Executor] = field(
        default=Factory(lambda self: self.futures_executor_fn(), takes_self=True)
    )

    def __del__(self) -> None:
        executor = self.futures_executor

        if executor is not None:
            self.futures_executor = None

            executor.shutdown(wait=True)
