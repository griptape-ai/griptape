from __future__ import annotations
import time
from typing import Any, Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attr import define, field
from griptape.tools.base_griptape_cloud_client import BaseGriptapeCloudClient
from griptape.utils.decorators import activity
from griptape.artifacts import InfoArtifact, TextArtifact, ErrorArtifact


@define
class GriptapeCloudStructureRunClient(BaseGriptapeCloudClient):
    """
    Attributes:
        description: LLM-friendly structure description.
        structure_id: ID of the Griptape Cloud Structure.
    """

    _description: Optional[str] = field(default=None, kw_only=True)
    structure_id: str = field(kw_only=True)
    structure_run_wait_time_interval: int = field(default=2, kw_only=True)
    structure_run_max_wait_time_attempts: int = field(default=20, kw_only=True)

    @activity(
        config={
            "description": "Can be used to execute a Run of a Structure with the following description: {{ _self.description }}",
            "schema": Schema(
                {Literal("args", description="A list of string arguments to submit to the Structure Run"): list}
            ),
        }
    )
    def execute_structure_run(self, params: dict) -> InfoArtifact | TextArtifact | ErrorArtifact:
        from requests import post, exceptions, HTTPError, Response

        args: list[str] = params["values"]["args"]
        url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/runs")

        try:
            response: Response = post(url, json={"args": args}, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            return self._get_structure_run_result(response_json["structure_run_id"])

        except (exceptions.RequestException, HTTPError) as err:
            return ErrorArtifact(str(err))

    def _get_structure_run_result(self, structure_run_id: str) -> InfoArtifact | TextArtifact | ErrorArtifact:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{structure_run_id}")

        result = self._get_structure_run_result_attempt(url)
        status = result.get("status")

        wait_attempts = 0
        while status in ["QUEUED", "RUNNING"] and wait_attempts < self.structure_run_max_wait_time_attempts:
            # wait
            time.sleep(self.structure_run_wait_time_interval)
            wait_attempts += 1
            result = self._get_structure_run_result_attempt(url)
            status = result.get("status")

        if wait_attempts >= self.structure_run_max_wait_time_attempts:
            return ErrorArtifact(
                f"Failed to get Run result after {self.structure_run_max_wait_time_attempts} attempts."
            )

        if status != "SUCCEEDED":
            return ErrorArtifact(result)

        if "output" in result:
            return TextArtifact(result["output"])
        else:
            return InfoArtifact("No output found in response")

    def _get_structure_run_result_attempt(self, structure_run_url: str) -> Any:
        from requests import get, Response

        response: Response = get(structure_run_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @property
    def description(self) -> str:
        if self._description is None:
            from requests import get

            url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/")

            response = get(url, headers=self.headers).json()
            if "description" in response:
                self._description = response["description"]
            else:
                raise ValueError(f'Error getting Structure description: {response["message"]}')

        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value
