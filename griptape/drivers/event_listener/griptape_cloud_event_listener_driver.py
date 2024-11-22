from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.events.base_event import BaseEvent


@define
class GriptapeCloudEventListenerDriver(BaseEventListenerDriver):
    """Driver for publishing events to Griptape Cloud.

    Attributes:
        base_url: The base URL of Griptape Cloud. Defaults to the GT_CLOUD_BASE_URL environment variable.
        api_key: The API key to authenticate with Griptape Cloud.
        headers: The headers to use when making requests to Griptape Cloud. Defaults to include the Authorization header.
        structure_run_id: The ID of the Structure Run to publish events to. Defaults to the GT_CLOUD_STRUCTURE_RUN_ID environment variable.
    """

    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
        kw_only=True,
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]), kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
    structure_run_id: Optional[str] = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_STRUCTURE_RUN_ID")), kw_only=True
    )

    @structure_run_id.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_run_id(self, _: Attribute, structure_run_id: str) -> None:
        if structure_run_id is None:
            raise ValueError(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID).",
            )

    def publish_event(self, event: BaseEvent | dict) -> None:
        from griptape.observability.observability import Observability

        event_payload = event.to_dict() if isinstance(event, BaseEvent) else event

        span_id = Observability.get_span_id()
        if span_id is not None:
            event_payload["span_id"] = span_id

        super().publish_event(event_payload)

    def try_publish_event_payload(self, event_payload: dict) -> None:
        self._post_event(self._get_event_request(event_payload))

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        self._post_event([self._get_event_request(event_payload) for event_payload in event_payload_batch])

    def _get_event_request(self, event_payload: dict) -> dict:
        return {
            "payload": event_payload,
            "timestamp": event_payload["timestamp"],
            "type": event_payload["type"],
        }

    def _post_event(self, json: list[dict] | dict) -> None:
        requests.post(
            url=urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/events"),
            json=json,
            headers=self.headers,
        ).raise_for_status()
