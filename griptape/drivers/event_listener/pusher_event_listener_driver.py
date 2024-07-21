from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BaseEventListenerDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from pusher import Pusher


@define
class PusherEventListenerDriver(BaseEventListenerDriver):
    app_id: str = field(kw_only=True)
    key: str = field(kw_only=True)
    secret: str = field(kw_only=True)
    cluster: str = field(kw_only=True)
    channel: str = field(kw_only=True)
    event_name: str = field(kw_only=True)
    pusher_client: Pusher = field(
        default=Factory(
            lambda self: import_optional_dependency("pusher").Pusher(
                app_id=self.app_id,
                key=self.key,
                secret=self.secret,
                cluster=self.cluster,
                ssl=True,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        data = [
            {"channel": self.channel, "name": self.event_name, "data": event_payload}
            for event_payload in event_payload_batch
        ]

        self.pusher_client.trigger_batch(data)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        self.pusher_client.trigger(channels=self.channel, event_name=self.event_name, data=event_payload)
