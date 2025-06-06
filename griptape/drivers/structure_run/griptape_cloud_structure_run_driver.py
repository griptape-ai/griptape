from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import requests
from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, InfoArtifact
from griptape.configs.defaults_config import Defaults
from griptape.drivers.structure_run import BaseStructureRunDriver
from griptape.events import BaseEvent, EventBus
from griptape.utils.griptape_cloud import griptape_cloud_url

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GriptapeCloudStructureRunDriver(BaseStructureRunDriver):
    base_url: str = field(default="https://cloud.griptape.ai", kw_only=True)
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
    structure_id: str = field(kw_only=True)
    structure_run_wait_time_interval: int = field(default=2, kw_only=True)
    structure_run_max_wait_time_attempts: int = field(default=20, kw_only=True)
    async_run: bool = field(default=False, kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact | InfoArtifact:
        structure_run_id = self._create_run(*args)

        if self.async_run:
            return InfoArtifact("Run started successfully")
        return self._get_run_result(structure_run_id)

    def _create_run(self, *args: BaseArtifact) -> str:
        url = griptape_cloud_url(self.base_url, f"api/structures/{self.structure_id}/runs")

        env_vars = [{"name": key, "value": value, "source": "manual"} for key, value in self.env.items()]

        response = requests.post(
            url,
            json={"args": [arg.value for arg in args], "env_vars": env_vars},
            headers=self.headers,
        )
        response.raise_for_status()
        response_json = response.json()

        return response_json["structure_run_id"]

    def _get_run_result(self, structure_run_id: str) -> BaseArtifact | InfoArtifact:
        events = self._get_run_events(structure_run_id)
        output = None

        for event in events:
            event_type = event["type"]
            event_payload = event.get("payload", {})
            if event["origin"] == "USER":
                try:
                    if "span_id" in event_payload:
                        span_id = event_payload.pop("span_id")
                        if "meta" in event_payload:
                            event_payload["meta"]["span_id"] = span_id
                        else:
                            event_payload["meta"] = {"span_id": span_id}
                    EventBus.publish_event(BaseEvent.from_dict(event_payload))
                except ValueError as e:
                    logger.warning("Failed to deserialize event: %s", e)
                if event["type"] == "FinishStructureRunEvent":
                    output = BaseArtifact.from_dict(event_payload["output_task_output"])
            elif event["origin"] == "SYSTEM":
                if event_type == "StructureRunError":
                    output = ErrorArtifact(event_payload["status_detail"]["error"])

        if output is None:
            raise ValueError("Output not found.")

        return output

    def _get_run_events(self, structure_run_id: str) -> Iterator[dict]:
        url = griptape_cloud_url(self.base_url, f"api/structure-runs/{structure_run_id}/events/stream")
        with requests.get(url, headers=self.headers, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        yield json.loads(decoded_line.removeprefix("data:").strip())
