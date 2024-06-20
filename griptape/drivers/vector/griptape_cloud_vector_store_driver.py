from urllib.parse import urljoin
import uuid
from typing import Optional, Any
from attrs import Factory, define, field
from dataclasses import dataclass
from griptape.drivers import BaseVectorStoreDriver
from griptape.utils import import_optional_dependency
from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from requests import post


@define
class GriptapeCloudVectorStoreDriver(BaseVectorStoreDriver):
    """A vector store driver for Griptape Cloud Knowledge Bases and Data Connectors.

    Attributes:
        api_key: API Key for Griptape Cloud.
        knowledge_base_id: Knowledge Base ID for Griptape Cloud.
        data_connector_ids: List of Data Connectors ID for Griptape Cloud.
        base_url: Base URL for Griptape Cloud.
        headers: Headers for Griptape Cloud.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    knowledge_base_id: str = field(kw_only=True, metadata={"serializable": True})
    data_connector_ids: list[str] = field(factory=list, kw_only=True, metadata={"serializable": True})
    base_url: str = field(default="https://cloud.griptape.ai", kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )

    @knowledge_base_id.validator  # pyright: ignore
    def validate_knowledge_base_id(self, _, knowledge_base_id: Optional[str]) -> None:
        # If data_connector_ids is provided, knowledge_base_id does not need to be provided.
        if self.data_connector_ids is not None:
            return

        # If data_connector_ids is not provided, knowledge_base_id is required.
        if knowledge_base_id is None:
            raise ValueError("An knowledge_base_id or data_connector_ids is required")

    @data_connector_ids.validator  # pyright: ignore
    def validate_data_connector_ids(self, _, data_connector_ids: Optional[list[str]]) -> None:
        # If knowledge_base_id is provided, data_connector_ids do not need to be provided.
        if self.knowledge_base_id is not None:
            return

        # data_connector_ids must be populated if provided.
        if (data_connector_ids is not None) and (len(data_connector_ids) == 0):
            raise ValueError("data_connector_ids must be populated if provided")

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
        namespace: Optional[str] = None,  # TODO: Remove this
        include_vectors: bool = False,
        distance_metric: str = "cosine_distance",
        # GriptapeCloudVectorStoreDriver-specific params:
        filter: Optional[dict] = None,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Performs a search on the Knowledge Base to find vectors similar to the provided input vector,
        optionally filtering to only those that match the provided namespace.
        """
        url = urljoin(self.base_url.strip("/"), f"/api/knowledge-bases/{self.knowledge_base_id}/query")

        request = {
            "query": query,
            "filters": {},
            "count": count,
            "include_vectors": include_vectors,
            "distance_metric": distance_metric,
            "filter": filter,
        }
        response_body = post(url, json=request, headers=self.headers).json()
        return response_body["query_results"]

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
