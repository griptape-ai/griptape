from __future__ import annotations

from attrs import define

from griptape.drivers import BaseEventListenerDriver


@define
class MockEventListenerDriver(BaseEventListenerDriver):
    def try_publish_event_payload(self, event_payload: dict) -> None:
        pass

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        pass
