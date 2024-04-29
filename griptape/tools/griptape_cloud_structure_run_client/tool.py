from __future__ import annotations
from typing import Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attr import define, field
from griptape.mixins.exponential_backoff_mixin import ExponentialBackoffMixin
from griptape.tools.base_griptape_cloud_client import BaseGriptapeCloudClient
from griptape.utils.decorators import activity
from griptape.artifacts import TextArtifact, ErrorArtifact


@define
class GriptapeCloudStructureRunClient(BaseGriptapeCloudClient, ExponentialBackoffMixin):
    """
    Attributes:
        description: LLM-friendly structure description.
        structure_id: ID of the Griptape Cloud Structure.
    """

    description: Optional[str] = field(default=None, kw_only=True)
    structure_id: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to execute a Run of a Structure with the following description: {{ _self._get_structure_description() }}",
            "schema": Schema(
                {Literal("args", description="A list of string arguments to submit to the Structure Run"): list}
            ),
        }
    )
    def execute_structure_run(self, params: dict) -> TextArtifact | ErrorArtifact:
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

    def _get_structure_run_result(self, structure_run_id: str) -> TextArtifact | ErrorArtifact:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{structure_run_id}")

        for attempt in self.retrying():
            with attempt:
                return self._get_structure_run_result_attempt(url)
        else:
            return ErrorArtifact("Failed to get Run result.")

    def _get_structure_run_result_attempt(self, structure_run_url: str) -> TextArtifact | ErrorArtifact:
        from requests import get, Response

        response: Response = get(structure_run_url, headers=self.headers)
        response.raise_for_status()
        content = response.json()

        status = content.get("status")

        if status in ("QUEUED", "RUNNING"):
            raise Exception("Structure Run is still in progress")

        if status != "SUCCEEDED":
            return ErrorArtifact(content)

        if "output" in content:
            return TextArtifact(content["output"])
        else:
            return ErrorArtifact("No output found in response")

    def _get_structure_description(self) -> str:
        if self.description:
            return self.description
        else:
            from requests import get

            url = urljoin(self.base_url.strip("/"), f"/api/structures/{self.structure_id}/")

            response = get(url, headers=self.headers).json()
            if "description" in response:
                return response["description"]
            else:
                raise ValueError(f'Error getting Structure description: {response["message"]}')
