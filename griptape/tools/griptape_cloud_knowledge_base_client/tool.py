from __future__ import annotations
from typing import Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attrs import define, field
from griptape.tools.base_griptape_cloud_client import BaseGriptapeCloudClient
from griptape.utils.decorators import activity
from griptape.artifacts import BaseArtifact, ListArtifact, TextArtifact, ErrorArtifact


@define
class GriptapeCloudKnowledgeBaseClient(BaseGriptapeCloudClient):
    """
    Attributes:
        description: LLM-friendly knowledge base description.
        knowledge_base_id: ID of the Griptape Cloud Knowledge Base.
    """

    description: Optional[str] = field(default=None, kw_only=True)
    knowledge_base_id: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to search a knowledge base with the following description: {{ _self._get_knowledge_base_description() }}",
            "schema": Schema(
                {
                    Literal(
                        "query", description="A natural language search query to run against the knowledge base"
                    ): str,
                    Literal(
                        "raw",
                        description="Return the raw artifacts from the knowledge base instead of a natural language response",
                    ): bool,
                }
            ),
        }
    )
    def query(self, params: dict) -> TextArtifact | ListArtifact | ErrorArtifact:
        from requests import post, exceptions

        query = params["values"]["query"]
        raw = params["values"].get("raw", False)
        url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/query")

        try:
            response = post(url, json={"query": query, "raw": raw}, headers=self.headers)

            if raw:
                response_body = response.json()
                artifacts: list[BaseArtifact] = []
                for query_result in response_body.get("result", []):
                    artifacts.append(BaseArtifact.from_json(query_result.meta["artifact"]))

                return ListArtifact(artifacts)
            else:
                return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    def _get_knowledge_base_description(self) -> str:
        from requests import get

        if self.description:
            return self.description
        else:
            url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/")

            response = get(url, headers=self.headers)
            response_body = response.json()
            if response.status_code == 200:
                if "description" in response_body:
                    return response_body["description"]
                else:
                    raise ValueError(
                        f"No description found for Knowledge Base {self.knowledge_base_id}. Please set a description, or manually set the `GriptapeCloudKnowledgeBaseClient.description` attribute."
                    )
            else:
                raise ValueError(f"Error accessing Knowledge Base {self.knowledge_base_id}.")
