from __future__ import annotations

import os
from typing import Literal, Optional
from urllib.parse import urljoin

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver
from griptape.events import BaseEvent, EventBus


@define
class GriptapeCloudStructureRunDriver(BaseStructureRunDriver):
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
    resource_type: Literal["structure", "assistant"] = field(default="structure", kw_only=True)
    resource_id: str = field(kw_only=True)
    run_wait_time_interval: int = field(default=2, kw_only=True)
    run_max_wait_time_attempts: int = field(default=20, kw_only=True)
    async_run: bool = field(default=False, kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact | InfoArtifact:
        from requests import Response, post

        url = urljoin(self.base_url.strip("/"), f"/api/{self.resource_type}s/{self.resource_id}/runs")

        env_vars = [{"name": key, "value": value, "source": "manual"} for key, value in self.env.items()]

        response: Response = post(
            url,
            json={"args": [arg.value for arg in args], "env_vars": env_vars, "stream": True},
            headers=self.headers,
        )
        response.raise_for_status()
        response_json = response.json()

        if self.async_run:
            return InfoArtifact("Run started successfully")
        else:
            return self._get_run_result(response_json[f"{self.resource_type}_run_id"])

    def _get_run_result(self, structure_run_id: str) -> BaseArtifact | InfoArtifact:
        url = urljoin(self.base_url.strip("/"), f"/api/{self.resource_type}-runs/{structure_run_id}")

        events, next_offset = self._get_run_events(url)

        output = None
        while not output:
            events, next_offset = self._get_run_events(url, offset=next_offset)
            for event in events:
                event_origin = event["origin"]
                if event_origin in ("ASSISTANT", "USER"):
                    EventBus.publish_event(BaseEvent.from_dict(event["payload"]))
                    if event["type"] == "FinishStructureRunEvent":
                        output = BaseArtifact.from_dict(event["payload"]["output_task_output"])
                elif event_origin == "SYSTEM":
                    if event["type"] == "StructureRunCompleted":
                        result = self._get_run_result_attempt(url)

                        if "output" in result:
                            output = BaseArtifact.from_dict(result["output"])
                        else:
                            output = InfoArtifact("No output found in response")
                    elif event["type"] == "StructureRunError":
                        result = self._get_run_result_attempt(url)

                        raise Exception(result["payload"]["status_detail"])

        return output

    def _get_run_events(self, structure_run_url: str, offset: int = 0) -> tuple[list[dict], int]:
        from requests import Response, get

        response: Response = get(f"{structure_run_url}/events", headers=self.headers, params={"offset": offset})
        response.raise_for_status()

        response_json = response.json()

        events = response_json["events"]
        next_offset = response_json["next_offset"]

        return events, next_offset

    def _get_run_result_attempt(self, structure_run_url: str) -> dict:
        from requests import Response, get

        response: Response = get(structure_run_url, headers=self.headers)
        response.raise_for_status()

        return response.json()
