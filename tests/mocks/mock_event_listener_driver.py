from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.drivers.event_listener import BaseEventListenerDriver

if TYPE_CHECKING:
    from collections.abc import Callable


@define
class MockEventListenerDriver(BaseEventListenerDriver):
    on_event_payload_publish: Callable[[dict], None] | None = field(default=None, kw_only=True)
    on_event_payload_batch_publish: Callable[[list[dict]], None] | None = field(default=None, kw_only=True)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        if self.on_event_payload_publish is not None:
            self.on_event_payload_publish(event_payload)

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        if self.on_event_payload_batch_publish is not None:
            self.on_event_payload_batch_publish(event_payload_batch)
