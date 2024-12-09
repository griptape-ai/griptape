from __future__ import annotations

import contextlib
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

    def __del__(self) -> None:
        executor = self.futures_executor

        if executor is not None:
            self.futures_executor = None  # pyright: ignore[reportAttributeAccessIssue] In practice this is safe, nobody will access this attribute after this point

            with contextlib.suppress(Exception):
                # don't raise exceptions in __del__
                executor.shutdown(wait=True)
