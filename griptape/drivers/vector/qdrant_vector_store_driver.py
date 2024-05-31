from __future__ import annotations
from typing import Optional, Any
from collections.abc import Iterable, Sequence, Generator
from attrs import define, field
import uuid
from itertools import islice
from griptape.drivers import BaseVectorStoreDriver
from griptape.artifacts import TextArtifact

from qdrant_client.http import models as rest

VECTOR_NAME = None
BATCH_SIZE = 64
DEFAULT_DISTANCE = "COSINE"


@define
class QdrantVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for Qdrant Vector DB."""

    location: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    host: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    port: Optional[int] = field(default=6333, kw_only=True, metadata={"serializable": True})
    grpc_port: Optional[int] = field(default=6334, kw_only=True, metadata={"serializable": True})
    prefer_grpc: Optional[bool] = field(default=False, kw_only=True, metadata={"serializable": True})
    force_recreate: Optional[bool] = field(default=True, kw_only=True, metadata={"serializable": True})
    distance: str = field(default=DEFAULT_DISTANCE, kw_only=True, metadata={"serializable": True})
    collection_name: str = field(kw_only=True, metadata={"serializable": True})
    vector_name: Optional[str] = VECTOR_NAME
    content_payload_key: str = field(default="data", kw_only=True, metadata={"serializable": True})
    # model: Any = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        from qdrant_client import QdrantClient, AsyncQdrantClient

        if self.location == ":memory:":
            self.client = AsyncQdrantClient(
                location=self.location,
                url=self.url,
                host=self.host,
                port=self.port,
                prefer_grpc=self.prefer_grpc,
                grpc_port=self.grpc_port,
            )
        else:
            self.client = QdrantClient(
                location=self.location,
                url=self.url,
                host=self.host,
                port=self.port,
                prefer_grpc=self.prefer_grpc,
                grpc_port=self.grpc_port,
            )
        # Ensure the collection exists and has the correct configuration
        self._create_collection(self.embedding_driver)

    def delete_vector(self, vector_id: str) -> None:
        """
        Delete vectors from the Qdrant collection based on their IDs.

        Parameters:
        - vector_ids: Optional list of vector IDs to delete.
        """
        deletion_response = self.client.delete(
            collection_name=self.collection_name, points_selector=rest.PointIdsList([vector_id])
        )
        if deletion_response.status == rest.UpdateStatus.COMPLETED:
            return f"Ids {vector_id} is successfully deleted"

    def query(
        self, query: str, count: Optional[int] = None, namespace: Optional[str] = None, include_vectors: bool = False
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """
        Query the Qdrant collection based on a query vector.

        Parameters:
        - query: Query string.
        - count: Optional number of results to return.
        - include_vectors: Whether to include vectors in the results.

        Returns:
        - List of QueryResult objects.
        """

        query_vector = self.embedding_driver.try_embed_chunk(query)

        # Create a search request
        limit = count
        with_payload = True
        with_vectors = True  # Ensure we get payloads in the results

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )

        # Convert results to QueryResult objects
        query_results = [
            BaseVectorStoreDriver.QueryResult(
                id=result.id,
                vector=result.vector if include_vectors else [],
                score=result.score,
                meta={k: v for k, v in result.payload.items() if k not in ["_score", "_tensor_facets"]},
            )
            for result in results
        ]
        # print(query_results)
        return query_results

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        content: Optional[str] = None,
    ) -> str:
        """
        Upsert vectors into the Qdrant collection.

        Parameters:
        - vector: The vector to be upserted.
        - vector_id: Optional vector ID.
        - namespace: Optional namespace for the vector.
        - meta: Optional dictionary containing metadata.
        - content: The text content to be included in the payload.
        """

        if vector_id is None:
            vector_id = str(uuid.uuid4())

        if meta is None:
            meta = {}

        if content:
            meta[self.content_payload_key] = content

        points = rest.Batch(ids=[vector_id], vectors=[vector], payloads=[meta] if meta else None)

        self.client.upsert(collection_name=self.collection_name, points=points)
        return vector_id

    def _create_collection(self, model: str) -> None:
        """
        Create a collection in Qdrant with the given model.

        Parameters:
        - model: Model for vector encoding.
        """
        from qdrant_client.models import Distance, VectorParams

        if self.force_recreate:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=len(model.try_embed_chunk("test_chunk")), distance=Distance.COSINE),
            )
        else:
            print(f"{self.collection_name} already exists. Use force_recreate=True to recreate the collection.")

    def _create_batches(
        self,
        texts: Iterable[TextArtifact],
        ids: Optional[Sequence[str]] = None,
        metadata: Optional[Sequence[dict[str, Any]]] = None,
        batch_size: int = BATCH_SIZE,
    ) -> Generator[tuple[list[str], list[rest.PointStruct]], None, None]:
        """
        Create batches of vectors for upsert operation.

        Parameters:
        - texts: Iterable of TextArtifact objects containing text data.
        - ids: Optional sequence of vector IDs.
        - metadata: Optional sequence of dictionaries containing metadata.
        - batch_size: Batch size for upsert operation.

        Returns:
        - Generator yielding batches of vectors.
        """
        from qdrant_client.http import models as rest

        texts_iterator = iter(texts)
        ids_iterator = iter(ids or [uuid.uuid4().hex for _ in iter(texts)])
        metadata_iterator = iter(metadata or [{} for _ in iter(texts)])

        while batch_texts := list(islice(texts_iterator, batch_size)):
            batch_ids = list(islice(ids_iterator, batch_size))
            batch_metadata = list(islice(metadata_iterator, batch_size))
            batch_text_values = [text.value for text in batch_texts]
            batch_embeddings = self.model.encode(batch_text_values)
            points = [
                rest.PointStruct(
                    id=point_id,
                    vector=vector if self.vector_name is None else {self.vector_name: vector},
                    payload={**payload, **meta},
                )
                for point_id, vector, payload, meta in zip(
                    batch_ids,
                    batch_embeddings,
                    self._build_payloads(batch_text_values, self.content_payload_key),
                    batch_metadata,
                )
            ]

            yield points

    def _build_payloads(self, texts: Iterable[str], content_payload_key: str) -> list[dict]:
        """
        Build payloads for vectors from text data.

        Parameters:
        - texts: Iterable of text data.
        - content_payload_key: Key for content payload.

        Returns:
        - List of payload dictionaries.
        """

        payloads = []
        for i, text in enumerate(texts):
            if text is None:
                raise ValueError(
                    "At least one of the texts is None. Please remove it before "
                    "calling .from_texts or .add_texts on Qdrant instance."
                )
            payloads.append({content_payload_key: text})
        return payloads

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        """
        Load a vector entry from the Qdrant collection based on its ID.

        Parameters:
        - vector_id: ID of the vector to load.
        - namespace: Optional namespace of the vector.

        Returns:
        - Vector entry.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} does not support loading the entry based on ID or namespace"
        )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        """
        Load vector entries from the Qdrant collection.

        Parameters:
        - namespace: Optional namespace of the vectors.

        Returns:
        - List of vector entries.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support loading entries based on IDs or namespaces"
        )
