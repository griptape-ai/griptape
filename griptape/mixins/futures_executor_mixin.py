from __future__ import annotations

import warnings
from abc import ABC
from concurrent import futures
from typing import Callable

from attrs import Factory, define, field


@define(slots=False, kw_only=True)
class FuturesExecutorMixin(ABC):
    create_futures_executor: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
    )

    _futures_executor: futures.Executor = field(
        default=Factory(
            lambda self: self.create_futures_executor(),
            takes_self=True,
        ),
        alias="futures_executor",
    )

    @property
    def futures_executor(self) -> futures.Executor:
        self.__raise_deprecation_warning()
        return self._futures_executor

    @futures_executor.setter
    def futures_executor(self, value: futures.Executor) -> None:
        self.__raise_deprecation_warning()
        self._futures_executor = value

    def __raise_deprecation_warning(self) -> None:
        warnings.warn(
            "`FuturesExecutorMixin.futures_executor` is deprecated and will be removed in a future release. Use `FuturesExecutorMixin.create_futures_executor` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
