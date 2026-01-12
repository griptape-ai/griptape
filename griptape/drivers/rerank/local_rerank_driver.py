from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Callable

from attrs import Factory, define, field

from griptape.configs.defaults_config import Defaults
from griptape.drivers.rerank import BaseRerankDriver
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin
from griptape.utils import execute_futures_list, with_contextvars

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact
    from griptape.drivers.embedding import BaseEmbeddingDriver


@define(kw_only=True)
class LocalRerankDriver(BaseRerankDriver, FuturesExecutorMixin):
    calculate_relatedness: Callable = field(
        default=Factory(lambda self: self._default_cosine_similarity, takes_self=True)
    )
    embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=Factory(lambda: Defaults.drivers_config.embedding_driver), metadata={"serializable": True}
    )

    @staticmethod
    def _default_cosine_similarity(x: list[float], y: list[float]) -> float:
        """Lazily import numpy and calculate cosine similarity."""
        from numpy import dot
        from numpy.linalg import norm

        return dot(x, y) / (norm(x) * norm(y))

    def run(self, query: str, artifacts: list[TextArtifact]) -> list[TextArtifact]:
        query_embedding = self.embedding_driver.embed(query, vector_operation="query")

        with self.create_futures_executor() as futures_executor:
            artifact_embeddings = execute_futures_list(
                [
                    futures_executor.submit(
                        with_contextvars(self.embedding_driver.embed_text_artifact), a, vector_operation="upsert"
                    )
                    for a in artifacts
                ],
            )

        artifacts_and_relatednesses = [
            (artifact, self.calculate_relatedness(query_embedding, artifact_embedding))
            for artifact, artifact_embedding in zip(artifacts, artifact_embeddings)
        ]

        artifacts_and_relatednesses.sort(key=operator.itemgetter(1), reverse=True)

        return [artifact for artifact, _ in artifacts_and_relatednesses]
