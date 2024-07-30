from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.drivers import BaseRerankDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from cohere import Client

    from griptape.artifacts import TextArtifact


@define(kw_only=True)
class CohereRerankDriver(BaseRerankDriver):
    model: str = field(default="rerank-english-v3.0", metadata={"serializable": True})
    top_n: Optional[int] = field(default=None)

    api_key: str = field(metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
    )

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        artifacts_dict = {str(hash(a.value)): a for a in artifacts}
        response = self.client.rerank(
            model=self.model,
            query=query,
            documents=[a.value for a in artifacts_dict.values()],
            return_documents=True,
            top_n=self.top_n,
        )

        return [artifacts_dict[str(hash(r.document.text))] for r in response.results]
