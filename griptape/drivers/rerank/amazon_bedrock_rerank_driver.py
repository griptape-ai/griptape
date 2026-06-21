from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.drivers.rerank.base_rerank_driver import BaseRerankDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import boto3
    from mypy_boto3_bedrock_agent_runtime.client import AgentsforBedrockRuntimeClient

    from griptape.artifacts import TextArtifact


@define(kw_only=True)
class AmazonBedrockRerankDriver(BaseRerankDriver):
    """Amazon Bedrock Rerank Driver for executing cross-encoder text scoring calculations serverlessly.

    Attributes:
        model: The specific model identifier ARN (e.g., 'cohere.rerank-v3-5:0').
        top_n: Optional maximum threshold number of sorted results to return.
        session: An authenticated boto3.Session connection profile container.
    """

    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()))
    model: str = field(default="cohere.rerank-v3-5:0")
    _client: AgentsforBedrockRuntimeClient | None = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )
    top_n: int | None = field(default=None, metadata={"serializable": True})

    @lazy_property()
    def client(self) -> AgentsforBedrockRuntimeClient:
        return self.session.client("bedrock-agent-runtime")

    @property
    def model_arn(self) -> str:
        region = self.session.region_name or "us-east-1"
        return f"arn:aws:bedrock:{region}::foundation-model/{self.model}"

    @classmethod
    def _post_process(cls, response: list, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        return [artifacts[res["index"]] for res in response]

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        truthy_artifacts = [a for a in artifacts if a]

        if not truthy_artifacts:
            return []

        sources = [
            {"type": "INLINE", "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": a.to_text()}}}
            for a in truthy_artifacts
        ]

        bedrock_reranking_configuration: dict[str, Any] = {"modelConfiguration": {"modelArn": self.model_arn}}
        if self.top_n is not None:
            bedrock_reranking_configuration["numberOfResults"] = self.top_n

        reranking_config = {
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": bedrock_reranking_configuration,
        }

        rerank_params = {
            "queries": [{"type": "TEXT", "textQuery": {"text": query}}],
            "sources": sources,
            "rerankingConfiguration": reranking_config,
        }

        response = self.client.rerank(**rerank_params)  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]

        all_results = response.get("results", [])

        while "nextToken" in response and response["nextToken"]:
            rerank_params["nextToken"] = response["nextToken"]

            response = self.client.rerank(**rerank_params)  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
            all_results.extend(response.get("results", []))

        return self._post_process(all_results, truthy_artifacts)
