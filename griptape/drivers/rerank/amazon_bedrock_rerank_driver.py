from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers.rerank.base_rerank_driver import BaseRerankDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import boto3
    from mypy_boto3_bedrock_agent_runtime.client import AgentsforBedrockRuntimeClient
    from mypy_boto3_bedrock_agent_runtime.type_defs import (
        BedrockRerankingConfigurationTypeDef,
        RerankingConfigurationTypeDef,
        RerankRequestTypeDef,
        RerankResultTypeDef,
        RerankSourceTypeDef,
    )

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
    model: str = field(default="cohere.rerank-v3-5:0", metadata={"serializable": True})
    _client: AgentsforBedrockRuntimeClient | None = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )
    top_n: int | None = field(default=None, metadata={"serializable": True})

    @lazy_property()
    def client(self) -> AgentsforBedrockRuntimeClient:
        return self.session.client("bedrock-agent-runtime")

    @property
    def model_arn(self) -> str:
        return f"arn:{self.client.meta.partition}:bedrock:{self.client.meta.region_name}::foundation-model/{self.model}"

    @staticmethod
    def _post_process(response: list[RerankResultTypeDef], artifacts: list[TextArtifact]) -> list[TextArtifact]:
        return [artifacts[res["index"]] for res in response]

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        truthy_artifacts = [artifact for artifact in artifacts if artifact]

        if not truthy_artifacts:
            return []

        sources: list[RerankSourceTypeDef] = [
            {
                "type": "INLINE",
                "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": artifact.to_text()}},
            }
            for artifact in truthy_artifacts
        ]

        bedrock_reranking_configuration: BedrockRerankingConfigurationTypeDef = {
            "modelConfiguration": {"modelArn": self.model_arn}
        }
        if self.top_n is not None:
            bedrock_reranking_configuration["numberOfResults"] = self.top_n

        reranking_config: RerankingConfigurationTypeDef = {
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": bedrock_reranking_configuration,
        }

        rerank_params: RerankRequestTypeDef = {
            "queries": [{"type": "TEXT", "textQuery": {"text": query}}],
            "sources": sources,
            "rerankingConfiguration": reranking_config,
        }

        response = self.client.rerank(**rerank_params)

        all_results = response["results"]

        while next_token := response.get("nextToken"):
            rerank_params["nextToken"] = next_token

            response = self.client.rerank(**rerank_params)
            all_results.extend(response["results"])

        return self._post_process(all_results, truthy_artifacts)
