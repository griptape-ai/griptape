from __future__ import annotations
from abc import ABC, abstractmethod
from concurrent import futures
from attr import define, field, Factory
from griptape.events import BaseEvent


@define
class BaseEventListenerDriver(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def publish_event(self, event: BaseEvent | dict) -> None:
        if isinstance(event, dict):
            self.futures_executor.submit(self.try_publish_event, event)
        else:
            self.futures_executor.submit(self.try_publish_event, event.to_dict())

    @abstractmethod
    def try_publish_event(self, event_payload: dict) -> None:
        ...
