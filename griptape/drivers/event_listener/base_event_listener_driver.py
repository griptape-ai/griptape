from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin

if TYPE_CHECKING:
    from griptape.events import BaseEvent

logger = logging.getLogger(__name__)


@define
class BaseEventListenerDriver(FuturesExecutorMixin, ABC):
    batched: bool = field(default=True, kw_only=True)
    batch_size: int = field(default=10, kw_only=True)

    _batch: list[dict] = field(default=Factory(list), kw_only=True)

    @property
    def batch(self) -> list[dict]:
        return self._batch

    def publish_event(self, event: BaseEvent | dict) -> None:
        event_payload = event if isinstance(event, dict) else event.to_dict()

        try:
            if self.batched:
                self._batch.append(event_payload)
                if len(self.batch) >= self.batch_size:
                    self._flush_events()
            else:
                self.futures_executor.submit(self.try_publish_event_payload, event_payload)
        except Exception as e:
            logger.error(e)

    def flush_events(self) -> None:
        if self.batch:
            self._flush_events()

    @abstractmethod
    def try_publish_event_payload(self, event_payload: dict) -> None: ...

    @abstractmethod
    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None: ...

    def _flush_events(self) -> None:
        self.futures_executor.submit(self.try_publish_event_payload_batch, self.batch)
        self._batch = []
