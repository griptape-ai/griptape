from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent import futures
from attr import define, field, Factory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.events import BaseEvent


@define
class BaseEventListenerDriver(ABC):
    futures_executor: futures.Executor = field(
        default=Factory(lambda: futures.ThreadPoolExecutor(max_workers=1)), kw_only=True
    )

    def publish_event(self, event: BaseEvent) -> None:
        self.futures_executor.submit(self.try_publish_event, event)

    @abstractmethod
    def try_publish_event(self, event: BaseEvent) -> None:
        ...
