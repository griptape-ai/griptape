from __future__ import annotations
from typing import Optional
from urllib.parse import urljoin
from schema import Schema, Literal
from attr import define, field, Factory
from griptape.tools import BaseTool
from griptape.utils.decorators import activity
from griptape.artifacts import TextArtifact, ErrorArtifact


@define
class GriptapeCloudKnowledgeBaseClient(BaseTool):
    """
    Attributes:
        description: LLM-friendly knowledge base description.
        base_url: Base URL for the Griptape Cloud Knowledge Base API.
        api_key: API key for Griptape Cloud.
        headers: Headers for the Griptape Cloud Knowledge Base API.
        knowledge_base_id: ID of the Griptape Cloud Knowledge Base.
    """

    description: Optional[str] = field(default=None, kw_only=True)
    base_url: str = field(default="https://cloud.griptape.ai", kw_only=True)
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
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
