from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3


@define
class AwsIotCoreEventListenerDriver(BaseEventListenerDriver):
    iot_endpoint: str = field(kw_only=True)
    topic: str = field(kw_only=True)
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    iotdata_client: Any = field(default=Factory(lambda self: self.session.client("iot-data"), takes_self=True))

    def try_publish_event_payload(self, event_payload: dict) -> None:
        self.iotdata_client.publish(topic=self.topic, payload=json.dumps(event_payload))

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        self.iotdata_client.publish(topic=self.topic, payload=json.dumps(event_payload_batch))
