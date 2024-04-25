from __future__ import annotations

import os
import requests

from urllib.parse import urljoin
from attr import define, field, Factory

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver
from griptape.events.base_event import BaseEvent


@define
class GriptapeCloudEventListenerDriver(BaseEventListenerDriver):
    """Driver for publishing events to Griptape Cloud.

    Attributes:
        base_url: The base URL of Griptape Cloud. Defaults to the GT_CLOUD_BASE_URL environment variable.
        api_key: The API key to authenticate with Griptape Cloud.
        headers: The headers to use when making requests to Griptape Cloud. Defaults to include the Authorization header.
        run_id: The ID of the Structure Run to publish events to. Defaults to the GT_CLOUD_STRUCTURE_RUN_ID environment variable.
    """

    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")), kw_only=True
    )
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    run_id: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_STRUCTURE_RUN_ID")), kw_only=True)

    @run_id.validator  # pyright: ignore
    def validate_run_id(self, _, run_id: str):
        if run_id is None:
            raise ValueError(
                "run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID)."
            )

    def try_publish_event(self, event: BaseEvent) -> None:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.run_id}/events")

        requests.post(url=url, json=event.to_dict(), headers=self.headers)
