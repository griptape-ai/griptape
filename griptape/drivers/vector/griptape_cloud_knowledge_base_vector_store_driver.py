from urllib.parse import urljoin
import requests
import uuid
from typing import Optional, Any
from attrs import Factory, define, field
from dataclasses import dataclass
from griptape.drivers import BaseEmbeddingDriver, BaseVectorStoreDriver, DummyEmbeddingDriver
from griptape.utils import import_optional_dependency
from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


@define
class GriptapeCloudKnowledgeBaseVectorStoreDriver(BaseVectorStoreDriver):
    """A vector store driver for Griptape Cloud Knowledge Bases and Data Connectors.

    Attributes:
        api_key: API Key for Griptape Cloud.
        knowledge_base_id: Knowledge Base ID for Griptape Cloud.
        base_url: Base URL for Griptape Cloud.
        headers: Headers for Griptape Cloud.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    knowledge_base_id: str = field(kw_only=True, metadata={"serializable": True})
    base_url: str = field(default="https://cloud.griptape.ai", kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: DummyEmbeddingDriver()), metadata={"serializable": True}, kw_only=True, init=False
    )

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not support vector upsert.")

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> BaseVectorStoreDriver.Entry:
        """Retrieves a specific vector entry from the collection based on its identifier and optional namespace."""
        raise NotImplementedError(f"{self.__class__.__name__} does not support entry loading.")

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        """Retrieves all vector entries from the collection, optionally filtering to only
        those that match the provided namespace.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support entry loading.")

    def query(
        self,
        query: str,
        count: Optional[int] = BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
        namespace: Optional[str] = None,
        include_vectors: Optional[bool] = False,
        distance_metric: Optional[str] = "cosine_distance",
        # GriptapeCloudKnowledgeBaseVectorStoreDriver-specific params:
        filter: Optional[dict] = None,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Performs a search on the Knowledge Base to find vectors similar to the provided input vector,
        optionally filtering to only those that match the provided filter(s).
        """
        url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/query")

        request = {
            "query": query,
            "count": count,
            "distance_metric": distance_metric,
            "filter": filter,
            "include_vectors": include_vectors,
        }
        return requests.post(url, json=request, headers=self.headers).json()

    def default_vector_model(self) -> Any:
        Vector = import_optional_dependency("pgvector.sqlalchemy").Vector
        Base = declarative_base()

        @dataclass
        class VectorModel(Base):
            __tablename__ = "embeddings"

            id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
            vector = Column(Vector())
            namespace = Column(String)
            meta = Column(JSON)

        return VectorModel

    def delete_vector(self, vector_id: str):
        raise NotImplementedError(f"{self.__class__.__name__} does not support deletion.")
