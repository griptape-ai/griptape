from __future__ import annotations

from abc import ABC
from concurrent import futures
from typing import Callable

from attrs import Factory, define, field


@define(slots=False, kw_only=True)
class FuturesExecutorMixin(ABC):
    create_futures_executor: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
    )

    futures_executor: futures.Executor = field(
        default=Factory(lambda self: self.create_futures_executor(), takes_self=True)
    )
