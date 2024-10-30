from __future__ import annotations

import os
from typing import Any, Literal, Optional
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
        url = urljoin(self.base_url.strip("/"), f"/api/{self.resource_type}-runs/{structure_run_id}/events")

        result = self._get_run_result_attempt(url)
        events = result["events"]
        offset = result["offset"]

        output = None
        while not output:
            result = self._get_run_result_attempt(url, offset=offset)
            events = result["events"]
            offset = result["next_offset"]
            for event in events:
                EventBus.publish_event(BaseEvent.from_dict(event["payload"]))
                if event["type"] == "FinishStructureRunEvent":
                    output = BaseArtifact.from_dict(event["payload"]["output_task_output"])
        return output

    def _get_run_result_attempt(self, structure_run_url: str, offset: int = 0) -> Any:
        from requests import Response, get

        response: Response = get(structure_run_url, headers=self.headers, params={"offset": offset})
        response.raise_for_status()

        return response.json()
