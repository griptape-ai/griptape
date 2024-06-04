from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from attrs import define, field
from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver

@define
class PusherEventListenerDriver(BaseEventListenerDriver):
    app_id: str = field(kw_only=True)
    key: str = field(kw_only=True)
    secret: str = field(kw_only=True)
    cluster: str = field(kw_only=True)

    # message specific
    channel: str = field(kw_only=True)
    event_name: str = field(kw_only=True)

    if TYPE_CHECKING:
        import pusher

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        pass

    def try_publish_event_payload(self, event_payload: dict) -> None:
        pusher_client = pusher.Pusher(
            app_id=self.app_id,
            key=self.key,
            secret=self.secret,
            cluster=self.cluster,
            ssl=True
        )

        pusher_client.trigger(
            channels=self.channel,
            event_name=self.event_name,
            data=json.dumps(event_payload)
        )