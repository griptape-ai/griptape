from __future__ import annotations

from typing import TYPE_CHECKING

from attr import Factory, define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.events.base_event import BaseEvent
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define
class AmazonSqsEventListenerDriver(BaseEventListenerDriver):
    queue_url: str = field(kw_only=True)
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)

    def try_publish_event(self, event: BaseEvent) -> None:
        self.session.client("sqs").send_message(QueueUrl=self.queue_url, MessageBody=event.to_json())
