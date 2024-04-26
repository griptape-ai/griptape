from __future__ import annotations

import requests

from attr import define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.events.base_event import BaseEvent


@define
class WebhookEventListenerDriver(BaseEventListenerDriver):
    webhook_url: str = field(kw_only=True)
    headers: dict = field(default=None, kw_only=True)

    def try_publish_event(self, event: BaseEvent) -> None:
        requests.post(url=self.webhook_url, json={"event": event.to_dict()}, headers=self.headers)
