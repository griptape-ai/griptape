from __future__ import annotations

from typing import Callable, Optional

from attrs import define, field

from griptape.drivers import BaseEventListenerDriver


@define
class MockEventListenerDriver(BaseEventListenerDriver):
    try_publish_event_payload_fn: Optional[Callable[[dict], None]] = field(default=None, kw_only=True)
    try_publish_event_payload_batch_fn: Optional[Callable[[list[dict]], None]] = field(default=None, kw_only=True)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        if self.try_publish_event_payload_fn is not None:
            self.try_publish_event_payload_fn(event_payload)

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        if self.try_publish_event_payload_batch_fn is not None:
            self.try_publish_event_payload_batch_fn(event_payload_batch)
