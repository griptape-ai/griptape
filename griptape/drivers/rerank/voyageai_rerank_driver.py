from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.drivers.rerank import BaseRerankDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from voyageai.client import Client

    from griptape.artifacts import TextArtifact


@define(kw_only=True)
class VoyageAiRerankDriver(BaseRerankDriver):
    """Voyage AI Rerank Driver.

    Attributes:
        model: Voyage AI rerank model name.
        api_key: API key to pass directly. Defaults to `VOYAGE_API_KEY` environment variable.
        top_k: Optional maximum number of results to return.
    """

    model: str = field(default="rerank-2.5", metadata={"serializable": True})
    api_key: str | None = field(default=None, metadata={"serializable": False})
    top_k: int | None = field(default=None, metadata={"serializable": True})
    _client: Client | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Any:
        return import_optional_dependency("voyageai").Client(api_key=self.api_key)

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        truthy_artifacts = [artifact for artifact in artifacts if artifact]

        if not truthy_artifacts:
            return []

        response = self.client.rerank(
            query=query,
            documents=[artifact.to_text() for artifact in truthy_artifacts],
            model=self.model,
            top_k=self.top_k,
        )

        return [truthy_artifacts[result.index] for result in response.results]
