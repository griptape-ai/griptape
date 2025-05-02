from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import requests
from attrs import define, field

from griptape.drivers.rerank.base_rerank_driver import BaseRerankDriver

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact


@define(kw_only=True)
class NvidiaNimRerankDriver(BaseRerankDriver):
    """Nvidia Rerank Driver."""

    model: str = field()
    base_url: str = field()
    truncate: Literal["NONE", "END"] = field(default="NONE")
    headers: dict = field(factory=dict)

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        if not artifacts:
            return []

        response = requests.post(
            url=f"{self.base_url.rstrip('/')}/v1/ranking",
            json=self._get_body(query, artifacts),
            headers=self.headers,
        )

        response.raise_for_status()

        ranked_artifacts = []
        for ranking in response.json()["rankings"]:
            artifact = artifacts[ranking["index"]]
            artifact.meta.update({"logit": ranking["logit"], "usage": ranking.get("usage")})
            ranked_artifacts.append(artifact)

        return ranked_artifacts

    def _get_body(self, query: str, artifacts: list[TextArtifact]) -> dict:
        return {
            "model": self.model,
            "query": {"text": query},
            "passages": [{"text": artifact.value} for artifact in artifacts],
            "truncate": self.truncate,
        }
