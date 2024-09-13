from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.drivers.structure_run.base_structure_run_driver import BaseStructureRunDriver


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
        from requests import Response, post

        url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/runs")

        env_vars = [{"name": key, "value": value, "source": "manual"} for key, value in self.env.items()]

        response: Response = post(
            url,
            json={"args": [arg.value for arg in args], "env_vars": env_vars},
            headers=self.headers,
        )
        response.raise_for_status()
        response_json = response.json()

        if self.async_run:
            return InfoArtifact("Run started successfully")
        else:
            return self._get_structure_run_result(response_json["structure_run_id"])

    def _get_structure_run_result(self, structure_run_id: str) -> BaseArtifact | InfoArtifact:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{structure_run_id}")

        result = self._get_structure_run_result_attempt(url)
        status = result["status"]

        wait_attempts = 0
        while (
            status not in ("SUCCEEDED", "FAILED", "ERROR", "CANCELLED")
            and wait_attempts < self.structure_run_max_wait_time_attempts
        ):
            # wait
            time.sleep(self.structure_run_wait_time_interval)
            wait_attempts += 1
            result = self._get_structure_run_result_attempt(url)
            status = result["status"]

        if wait_attempts >= self.structure_run_max_wait_time_attempts:
            raise Exception(f"Failed to get Run result after {self.structure_run_max_wait_time_attempts} attempts.")

        if status != "SUCCEEDED":
            raise Exception(f"Run failed with status: {status}")

        if "output" in result:
            return BaseArtifact.from_dict(result["output"])
        else:
            return InfoArtifact("No output found in response")

    def _get_structure_run_result_attempt(self, structure_run_url: str) -> Any:
        from requests import Response, get

        response: Response = get(structure_run_url, headers=self.headers)
        response.raise_for_status()

        return response.json()
