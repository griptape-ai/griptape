from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent import futures
from attr import define, field, Factory


@define
class BaseEventListenerDriver(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def publish_event(self, event_payload: dict) -> None:
        self.futures_executor.submit(self.try_publish_event, event_payload)

    @abstractmethod
    def try_publish_event(self, event_payload: dict) -> None:
        ...
