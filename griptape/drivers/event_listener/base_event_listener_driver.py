from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from concurrent import futures
from typing import TYPE_CHECKING, Callable

from attrs import Factory, define, field

if TYPE_CHECKING:
    from griptape.events import BaseEvent

logger = logging.getLogger(__name__)


@define
class BaseEventListenerDriver(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()),
        kw_only=True,
    )
    batched: bool = field(default=True, kw_only=True)
    batch_size: int = field(default=10, kw_only=True)

    _batch: list[dict] = field(default=Factory(list), kw_only=True)

    @property
    def batch(self) -> list[dict]:
        return self._batch

    def publish_event(self, event: BaseEvent | dict, *, flush: bool = False) -> None:
        with self.futures_executor_fn() as executor:
            executor.submit(self._safe_try_publish_event, event, flush=flush)

    @abstractmethod
    def try_publish_event_payload(self, event_payload: dict) -> None: ...

    @abstractmethod
    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None: ...

    def _safe_try_publish_event(self, event: BaseEvent | dict, *, flush: bool) -> None:
        try:
            event_payload = event if isinstance(event, dict) else event.to_dict()

            if self.batched:
                self._batch.append(event_payload)
                if len(self.batch) >= self.batch_size or flush:
                    self.try_publish_event_payload_batch(self.batch)
                    self._batch = []
                return
            else:
                self.try_publish_event_payload(event_payload)
        except Exception as e:
            logger.error(e)
