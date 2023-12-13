from __future__ import annotations
import json
import logging
import numpy as np
from griptape.utils import import_optional_dependency
from typing import Optional, List, TYPE_CHECKING
from attr import define, field, Factory
from griptape.drivers import BaseVectorStoreDriver

logging.basicConfig(level=logging.WARNING)


if TYPE_CHECKING:
    from redis import Redis


@define
class RedisVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for Redis.

    This driver interfaces with a Redis instance and utilizes the Redis hashes and RediSearch module to store, retrieve, and query vectors in a structured manner.
    Proper setup of the Redis instance and RediSearch is necessary for the driver to function correctly.

    Attributes:
        host: The host of the Redis instance.
        port: The port of the Redis instance.
        db: The database of the Redis instance.
        password: The password of the Redis instance.
        index: The name of the index to use.
    """

    host: str = field(kw_only=True)
    port: int = field(kw_only=True)
    db: int = field(kw_only=True, default=0)
    password: str | None = field(default=None, kw_only=True)
    index: str = field(kw_only=True)

    client: Redis = field(
        default=Factory(
            lambda self: import_optional_dependency("redis").Redis(
                host=self.host, port=self.port, db=self.db, password=self.password, decode_responses=False
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
        """Inserts or updates a vector in Redis.

        If a vector with the given vector ID already exists, it is updated; otherwise, a new vector is inserted.
        Metadata associated with the vector can also be provided.
        """
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        key = self._generate_key(vector_id, namespace)
        bytes_vector = json.dumps(vector).encode("utf-8")

        mapping = {"vector": np.array(vector, dtype=np.float32).tobytes(), "vec_string": bytes_vector}

        if meta:
            mapping["metadata"] = json.dumps(meta)

        self.client.hset(key, mapping=mapping)

        return vector_id

    def load_entry(self, vector_id: str, namespace: str | None = None) -> BaseVectorStoreDriver.Entry | None:
        """Retrieves a specific vector entry from Redis based on its identifier and optional namespace.

        Returns:
            If the entry is found, it returns an instance of BaseVectorStoreDriver.Entry; otherwise, None is returned.
        """
        key = self._generate_key(vector_id, namespace)
        result = self.client.hgetall(key)
        vector = np.frombuffer(result[b"vector"], dtype=np.float32).tolist()
        meta = json.loads(result[b"metadata"]) if b"metadata" in result else None

        return BaseVectorStoreDriver.Entry(id=vector_id, meta=meta, vector=vector, namespace=namespace)

    def load_entries(self, namespace: str | None = None) -> list[BaseVectorStoreDriver.Entry]:
        """Retrieves all vector entries from Redis that match the optional namespace.

        Returns:
            A list of `BaseVectorStoreDriver.Entry` objects.
        """
        pattern = f"{namespace}:*" if namespace else "*"
        keys = self.client.keys(pattern)

        return [self.load_entry(key.decode("utf-8"), namespace=namespace) for key in keys]

    def query(
        self, query: str, count: int | None = None, namespace: str | None = None, **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Performs a nearest neighbor search on Redis to find vectors similar to the provided input vector.

        Results can be limited using the count parameter and optionally filtered by a namespace.

        Returns:
            A list of BaseVectorStoreDriver.QueryResult objects, each encapsulating the retrieved vector, its similarity score, metadata, and namespace.
        """
        Query = import_optional_dependency("redis.commands.search.query").Query

        vector = self.embedding_driver.embed_string(query)

        query_expression = (
            Query(f"*=>[KNN {count or 10} @vector $vector as score]")
            .sort_by("score")
            .return_fields("id", "score", "metadata", "vec_string")
            .paging(0, count or 10)
            .dialect(2)
        )

        query_params = {"vector": np.array(vector, dtype=np.float32).tobytes()}

        results = self.client.ft(self.index).search(query_expression, query_params).docs

        query_results = []
        for document in results:
            metadata = getattr(document, "metadata", None)
            namespace = document.id.split(":")[0] if ":" in document.id else None
            vector_id = document.id.split(":")[1] if ":" in document.id else document.id
            vector_float_list = json.loads(document["vec_string"])
            query_results.append(
                BaseVectorStoreDriver.QueryResult(
                    id=vector_id,
                    vector=vector_float_list,
                    score=float(document["score"]),
                    meta=metadata,
                    namespace=namespace,
                )
            )
        return query_results

    def create_index(self, namespace: str | None = None, vector_dimension: int | None = None) -> None:
        """Creates a new index in Redis with the specified properties.

        If an index with the given name already exists, a warning is logged and the method does not proceed.
        The method expects the dimension of the vectors (i.e., vector_dimension) that will be stored in this index.
        Optionally, a namespace can be provided which will determine the prefix for document keys.
        The index is constructed with a TagField named "tag" and a VectorField that utilizes the cosine distance metric on FLOAT32 type vectors.
        """
        TagField = import_optional_dependency("redis.commands.search.field").TagField
        VectorField = import_optional_dependency("redis.commands.search.field").VectorField
        IndexDefinition = import_optional_dependency("redis.commands.search.indexDefinition").IndexDefinition
        IndexType = import_optional_dependency("redis.commands.search.indexDefinition").IndexType

        try:
            self.client.ft(self.index).info()
            logging.warning("Index already exists!")
        except:
            schema = (
                TagField("tag"),
                VectorField(
                    "vector", "FLAT", {"TYPE": "FLOAT32", "DIM": vector_dimension, "DISTANCE_METRIC": "COSINE"}
                ),
            )

            doc_prefix = self._get_doc_prefix(namespace)
            definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.HASH)
            self.client.ft(self.index).create_index(fields=schema, definition=definition)

    def _generate_key(self, vector_id: str, namespace: str | None = None) -> str:
        """Generates a Redis key using the provided vector ID and optionally a namespace."""
        return f"{namespace}:{vector_id}" if namespace else vector_id

    def _get_doc_prefix(self, namespace: str | None = None) -> str:
        """Get the document prefix based on the provided namespace."""
        return f"{namespace}:" if namespace else ""
