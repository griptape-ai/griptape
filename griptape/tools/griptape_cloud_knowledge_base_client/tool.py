from __future__ import annotations
from typing import Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attrs import define, field
from griptape.tools.base_griptape_cloud_client import BaseGriptapeCloudClient
from griptape.utils.decorators import activity
from griptape.artifacts import TextArtifact, ErrorArtifact


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
                {Literal("query", description="A natural language search query to run against the knowledge base"): str}
            ),
        }
    )
    def query(self, params: dict) -> TextArtifact | ErrorArtifact:
        from requests import post, exceptions

        query = params["values"]["query"]
        url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/query")

        try:
            response = post(url, json={"query": query}, headers=self.headers)

            return TextArtifact(response.text)
        except exceptions.RequestException as err:
            return ErrorArtifact(str(err))

    def _get_knowledge_base_description(self) -> str:
        from requests import get

        if self.description:
            return self.description
        else:
            url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/")

            response = get(url, headers=self.headers).json()
            if "description" in response:
                return response["description"]
            else:
                raise ValueError(f'Error getting Knowledge Base description: {response["message"]}')
