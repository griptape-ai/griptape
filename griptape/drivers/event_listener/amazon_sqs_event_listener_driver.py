from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define
class AmazonSqsEventListenerDriver(BaseEventListenerDriver):
    queue_url: str = field(kw_only=True)
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    sqs_client: Any = field(default=Factory(lambda self: self.session.client("sqs"), takes_self=True))

    def try_publish_event_payload(self, event_payload: dict) -> None:
        self.sqs_client.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(event_payload))

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        entries = [
            {"Id": str(event_payload["id"]), "MessageBody": json.dumps(event_payload)}
            for event_payload in event_payload_batch
        ]

        self.sqs_client.send_message_batch(QueueUrl=self.queue_url, Entries=entries)
