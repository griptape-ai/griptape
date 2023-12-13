from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING
from griptape import utils
import logging
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseVectorStoreDriver
from attr import define, field, Factory

if TYPE_CHECKING:
    from opensearchpy import OpenSearch


@define
class OpenSearchVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for OpenSearch.

    Attributes:
        host: The host of the OpenSearch cluster.
        port: The port of the OpenSearch cluster.
        http_auth: The HTTP authentication credentials to use.
        use_ssl: Whether to use SSL.
        verify_certs: Whether to verify SSL certificates.
        index_name: The name of the index to use.
    """

    host: str = field(kw_only=True)
    port: int = field(default=443, kw_only=True)
    http_auth: str | tuple[str, str] | None = field(default=None, kw_only=True)
    use_ssl: bool = field(default=True, kw_only=True)
    verify_certs: bool = field(default=True, kw_only=True)
    index_name: str = field(kw_only=True)

    client: OpenSearch = field(
        default=Factory(
            lambda self: import_optional_dependency("opensearchpy").OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_auth=self.http_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=import_optional_dependency("opensearchpy").RequestsHttpConnection,
            ),
            takes_self=True,
        )
    )

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: str | None = None,
        namespace: str | None = None,
        meta: dict | None = None,
        **kwargs,
    ) -> str:
        """Inserts or updates a vector in OpenSearch.

        If a vector with the given vector ID already exists, it is updated; otherwise, a new vector is inserted.
        Metadata associated with the vector can also be provided.
        """

        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        doc = {"vector": vector, "namespace": namespace, "metadata": meta}
        doc.update(kwargs)
        response = self.client.index(index=self.index_name, id=vector_id, body=doc)

        return response["_id"]

    def load_entry(self, vector_id: str, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        """Retrieves a specific vector entry from OpenSearch based on its identifier and optional namespace.

        Returns:
            If the entry is found, it returns an instance of BaseVectorStoreDriver.Entry; otherwise, None is returned.
        """
        try:
            query = {"bool": {"must": [{"term": {"_id": vector_id}}]}}

            if namespace:
                query["bool"]["must"].append({"term": {"namespace": namespace}})

            response = self.client.search(index=self.index_name, body={"query": query, "size": 1})

            if response["hits"]["total"]["value"] > 0:
                vector_data = response["hits"]["hits"][0]["_source"]
                entry = BaseVectorStoreDriver.Entry(
                    id=vector_id,
                    meta=vector_data.get("metadata"),
                    vector=vector_data.get("vector"),
                    namespace=vector_data.get("namespace"),
                )
                return entry
            else:
                return None
        except Exception as e:
            logging.error(f"Error while loading entry: {e}")
            return None

    def load_entries(self, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        """Retrieves all vector entries from OpenSearch that match the optional namespace.

        Returns:
            A list of BaseVectorStoreDriver.Entry objects.
        """

        query_body = {"size": 10000, "query": {"match_all": {}}}

        if namespace:
            query_body["query"] = {"match": {"namespace": namespace}}

        response = self.client.search(index=self.index_name, body=query_body)

        entries = [
            BaseVectorStoreDriver.Entry(
                id=hit["_id"],
                vector=hit["_source"].get("vector"),
                meta=hit["_source"].get("metadata"),
                namespace=hit["_source"].get("namespace"),
            )
            for hit in response["hits"]["hits"]
        ]
        return entries

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        include_metadata=True,
        field_name: str = "vector",
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Performs a nearest neighbor search on OpenSearch to find vectors similar to the provided query string.

        Results can be limited using the count parameter and optionally filtered by a namespace.

        Returns:
            A list of BaseVectorStoreDriver.QueryResult objects, each encapsulating the retrieved vector, its similarity score, metadata, and namespace.
        """
        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT
        vector = self.embedding_driver.embed_string(query)
        # Base k-NN query
        query_body = {"size": count, "query": {"knn": {field_name: {"vector": vector, "k": count}}}}

        if namespace:
            query_body["query"] = {
                "bool": {
                    "must": [{"match": {"namespace": namespace}}, {"knn": {field_name: {"vector": vector, "k": count}}}]
                }
            }

        response = self.client.search(index=self.index_name, body=query_body)

        return [
            BaseVectorStoreDriver.QueryResult(
                id=hit["_id"],
                namespace=hit["_source"].get("namespace") if namespace else None,
                score=hit["_score"],
                vector=hit["_source"].get("vector") if include_vectors else None,
                meta=hit["_source"].get("metadata") if include_metadata else None,
            )
            for hit in response["hits"]["hits"]
        ]

    def create_index(self, vector_dimension: int | None = None, settings_override: dict | None = None) -> None:
        """Creates a new vector index in OpenSearch.

        The index is structured to support k-NN (k-nearest neighbors) queries.

        Args:
            vector_dimension: The dimension of vectors that will be stored in this index.

        """
        default_settings = {"number_of_shards": 1, "number_of_replicas": 1, "index.knn": True}

        if settings_override:
            default_settings.update(settings_override)

        try:
            if self.client.indices.exists(index=self.index_name):
                logging.warning("Index already exists!")
                return
            else:
                mapping = {
                    "settings": default_settings,
                    "mappings": {
                        "properties": {
                            "vector": {"type": "knn_vector", "dimension": vector_dimension},
                            "namespace": {"type": "keyword"},
                            "metadata": {"type": "object", "enabled": True},
                        }
                    },
                }

                self.client.indices.create(index=self.index_name, body=mapping)
        except Exception as e:
            logging.error(f"Error while handling index: {e}")
