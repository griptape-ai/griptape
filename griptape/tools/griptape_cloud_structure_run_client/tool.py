from __future__ import annotations
import time
from typing import List, Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attr import define, field
from griptape.tools.base_griptape_cloud_client import BaseGriptapeCloudClient
from griptape.utils.decorators import activity
from griptape.artifacts import TextArtifact, ErrorArtifact


@define
class GriptapeCloudStructureRunClient(BaseGriptapeCloudClient):
    """
    Attributes:
        description: LLM-friendly structure description.
        structure_id: ID of the Griptape Cloud Structure.
        structure_run_wait_time_attempts: Number of attempts to wait for the structure run to complete.
        structure_run_wait_time_multiplier: Multiplier for the wait time between attempts.
    """

    description: Optional[str] = field(default=None, kw_only=True)
    structure_id: str = field(kw_only=True)
    structure_run_wait_time_attempts: int = field(default=20, kw_only=True)
    structure_run_wait_time_multiplier: float = field(default=1.5, kw_only=True)

    @activity(
        config={
            "description": "Can be used to submit a run to a structure with the following description: {{ _self._get_structure_description() }}",
            "schema": Schema(
                {Literal("args", description="A list of arguments to submit to the structure run"): list[str]}
            ),
        }
    )
    def submit_structure_run(self, params: dict) -> TextArtifact | ErrorArtifact:
        from requests import post, exceptions

        args: list[str] = params["values"]["args"]
        url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/runs")

        try:
            response = post(url, json={"args": args}, headers=self.headers)

            return TextArtifact(response.json())
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    @activity(
        config={
            "description": "Can be used to get the result of a structure run",
            "schema": Schema({Literal("structure_run_id", description="The ID of the structure run"): str}),
        }
    )
    def get_structure_run_result(self, params: dict) -> TextArtifact | ErrorArtifact:
        from requests import get, exceptions

        structure_run_id = params["values"]["structure_run_id"]
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{structure_run_id}")

        try:
            response = get(url, headers=self.headers)
            content = response.json()

            status = content.get("status")

            wait_time = 1
            wait_attempts = 0
            while status in ["QUEUED", "RUNNING"] and wait_attempts < self.structure_run_wait_time_attempts:
                # wait
                time.sleep(wait_time)
                wait_time = wait_time * self.structure_run_wait_time_multiplier
                wait_attempts += 1

                response = get(url, headers=self.headers)
                content = response.json()
                status = content.get("status")

            if status != "SUCCEEDED":
                return ErrorArtifact(content)

            if "output" in content:
                return TextArtifact(content["output"])
            else:
                return ErrorArtifact("No output found in response")

        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    def _get_structure_description(self) -> str:
        from requests import get

        if self.description:
            return self.description
        else:
            url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/")

            response = get(url, headers=self.headers).json()
            if "description" in response:
                return response["description"]
            else:
                raise ValueError(f'Error getting Structure description: {response["message"]}')
