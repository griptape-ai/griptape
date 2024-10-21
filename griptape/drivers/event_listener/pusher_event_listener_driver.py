from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.drivers import BaseEventListenerDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from pusher import Pusher


@define
class PusherEventListenerDriver(BaseEventListenerDriver):
    app_id: str = field(kw_only=True, metadata={"serializable": True})
    key: str = field(kw_only=True, metadata={"serializable": True})
    secret: str = field(kw_only=True, metadata={"serializable": False})
    cluster: str = field(kw_only=True, metadata={"serializable": True})
    channel: str = field(kw_only=True, metadata={"serializable": True})
    event_name: str = field(kw_only=True, metadata={"serializable": True})
    ssl: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    _client: Optional[Pusher] = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Pusher:
        return import_optional_dependency("pusher").Pusher(
            app_id=self.app_id,
            key=self.key,
            secret=self.secret,
            cluster=self.cluster,
            ssl=self.ssl,
        )

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        data = [
            {"channel": self.channel, "name": self.event_name, "data": event_payload}
            for event_payload in event_payload_batch
        ]

        self.client.trigger_batch(data)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        self.client.trigger(channels=self.channel, event_name=self.event_name, data=event_payload)
