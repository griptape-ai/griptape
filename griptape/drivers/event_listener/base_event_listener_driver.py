from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent import futures
from logging import Logger

from attr import Factory, define, field

from griptape.events import BaseEvent

logger = Logger(__name__)


@define
class BaseEventListenerDriver(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()), kw_only=True)

    def publish_event(self, event: BaseEvent | dict) -> None:
        if isinstance(event, dict):
            self.futures_executor.submit(self._safe_try_publish_event_payload, event)
        else:
            self.futures_executor.submit(self._safe_try_publish_event_payload, event.to_dict())

    @abstractmethod
    def try_publish_event_payload(self, event_payload: dict) -> None:
        ...

    def _safe_try_publish_event_payload(self, event_payload: dict) -> None:
        try:
            self.try_publish_event_payload(event_payload)
        except Exception as e:
            logger.error(e)
