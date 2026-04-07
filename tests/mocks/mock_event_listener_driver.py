from __future__ import annotations

from typing import Callable, Optional

from attrs import define, field

from griptape.drivers.event_listener import BaseEventListenerDriver


@define
class MockEventListenerDriver(BaseEventListenerDriver):
    on_event_payload_publish: Optional[Callable[[dict], None]] = field(default=None, kw_only=True)
    on_event_payload_batch_publish: Optional[Callable[[list[dict]], None]] = field(default=None, kw_only=True)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        if self.on_event_payload_publish is not None:
            self.on_event_payload_publish(event_payload)

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        if self.on_event_payload_batch_publish is not None:
            self.on_event_payload_batch_publish(event_payload_batch)
