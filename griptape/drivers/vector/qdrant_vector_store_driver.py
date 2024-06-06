from __future__ import annotations
from typing import Optional
from attrs import define, field
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
from griptape.utils import import_optional_dependency
from qdrant_client.http import models as rest

VECTOR_NAME = None
BATCH_SIZE = 64
DEFAULT_DISTANCE = "COSINE"


@define
class QdrantVectorStoreDriver(BaseVectorStoreDriver):
    """
    Attributes:
        location: An optional location for the Qdrant client. If set to ':memory:', an in-memory client is used.
        url: An optional Qdrant API URL.
        host: An optional Qdrant host.
        port: The port number for the Qdrant client. Defaults to 6333.
        grpc_port: The gRPC port number for the Qdrant client. Defaults to 6334.
        prefer_grpc: A boolean indicating whether to prefer gRPC over HTTP. Defaults to False.
        force_recreate: A boolean indicating whether to force recreation of the collection. Defaults to True.
        distance: The distance metric to be used for the vectors. Defaults to 'COSINE'.
        collection_name: The name of the Qdrant collection.
        vector_name: An optional name for the vectors.
        content_payload_key: The key for the content payload in the metadata. Defaults to 'data'.
    """

    location: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    host: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    port: int = field(default=6333, kw_only=True, metadata={"serializable": True})
    grpc_port: int = field(default=6334, kw_only=True, metadata={"serializable": True})
    prefer_grpc: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    force_recreate: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    distance: str = field(default=DEFAULT_DISTANCE, kw_only=True, metadata={"serializable": True})
    collection_name: str = field(kw_only=True, metadata={"serializable": True})
    vector_name: Optional[str] = VECTOR_NAME
    content_payload_key: str = field(default="data", kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self) -> None:
        if self.location == ":memory:":
            self.client = import_optional_dependency("qdrant_client").AsyncQdrantClient(
                location=self.location,
                url=self.url,
                host=self.host,
                port=self.port,
                prefer_grpc=self.prefer_grpc,
                grpc_port=self.grpc_port,
            )
        else:
            self.client = import_optional_dependency("qdrant_client").QdrantClient(
                location=self.location,
                url=self.url,
                host=self.host,
                port=self.port,
                prefer_grpc=self.prefer_grpc,
                grpc_port=self.grpc_port,
            )

    def delete_vector(self, vector_id: str) -> None:
        """
        Delete a vector from the Qdrant collection based on its ID.

        Parameters:
            vector_id (str): ID of the vector to delete.
        """
        try:
            deletion_response = self.client.delete(
                collection_name=self.collection_name, points_selector=rest.PointIdsList([vector_id])
            )
            if deletion_response.status == rest.UpdateStatus.COMPLETED:
                print(f"ID {vector_id} is successfully deleted")
            else:
                print(f"Failed to delete ID {vector_id}. Status: {deletion_response.status}")
        except Exception as e:
            print(f"An error occurred while trying to delete ID {vector_id}: {e}")

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        with_payload: bool = True,
        with_vectors: bool = True,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """
        Query the Qdrant collection based on a query vector.

        Parameters:
            query (str): Query string.
            count (Optional[int]): Optional number of results to return.
            namespace (Optional[str]): Optional namespace of the vectors.
            include_vectors (bool): Whether to include vectors in the results.

        Returns:
            list[BaseVectorStoreDriver.QueryResult]: List of QueryResult objects.
        """
        query_vector = self.embedding_driver.embed_string(query)

        # Create a search request
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=count,
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
            vector (list[float]): The vector to be upserted.
            vector_id (Optional[str]): Optional vector ID.
            namespace (Optional[str]): Optional namespace for the vector.
            meta (Optional[dict]): Optional dictionary containing metadata.
            content (Optional[str]): The text content to be included in the payload.

        Returns:
            str: The ID of the upserted vector.
        """

        if vector_id is None:
            vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))

        if meta is None:
            meta = {}

        if content:
            meta[self.content_payload_key] = content

        points = rest.Batch(ids=[vector_id], vectors=[vector], payloads=[meta] if meta else None)

        self.client.upsert(collection_name=self.collection_name, points=points)
        return vector_id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        """
        Load a vector entry from the Qdrant collection based on its ID.

        Parameters:
            vector_id (str): ID of the vector to load.
            namespace (str, optional): Optional namespace of the vector.

        Returns:
            Optional[BaseVectorStoreDriver.Entry]: Vector entry if found, else None.
        """
        try:
            results = self.client.retrieve(
                collection_name=self.collection_name, ids=[vector_id], with_payload=True, with_vectors=True
            )
            if results:
                entry = results[0]
                return BaseVectorStoreDriver.Entry(
                    id=entry.id,
                    vector=entry.vector,
                    meta={k: v for k, v in entry.payload.items() if k not in ["_score", "_tensor_facets"]},
                )
            else:
                return None
        except Exception as e:
            print(f"An error occurred while trying to retrieve the vector by ID: {e}")
            return None

    def load_entries(
        self, ids: list[str], with_payload: bool = True, with_vectors: bool = True, namespace: Optional[str] = None
    ) -> list[BaseVectorStoreDriver.Entry]:
        """
        Load vector entries from the Qdrant collection.

        Parameters:
            namespace: Optional namespace of the vectors.
            ids (list[str]): List of IDs to lookup.
            with_payload (bool): Specify which stored payload should be attached to the result.
            with_vectors (bool): Whether to attach stored vectors to the search result.

        Returns:
            List of points.
        """
        try:
            results = self.client.retrieve(
                collection_name=self.collection_name, ids=ids, with_payload=with_payload, with_vectors=with_vectors
            )
            return [
                BaseVectorStoreDriver.Entry(
                    id=entry.id,
                    vector=entry.vector if with_vectors else [],
                    meta={k: v for k, v in entry.payload.items() if k not in ["_score", "_tensor_facets"]},
                )
                for entry in results
            ]
        except Exception as e:
            print(f"An error occurred while trying to retrieve points by IDs: {e}")
            return []
