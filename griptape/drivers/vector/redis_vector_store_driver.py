from typing import Optional, List
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
import redis
from attr import define, field
import json
from redis.commands.search.query import Query


@define
class RedisVectorStoreDriver(BaseVectorStoreDriver):
    INDEX_NAME = "your_index_name_here"
    host: str = field(kw_only=True)
    port: int = field(kw_only=True)
    db: int = field(kw_only=True, default=0)
    password: Optional[str] = field(default=None, kw_only=True)
    client: redis.StrictRedis = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.client = redis.StrictRedis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password
        )

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        vector_id = vector_id if vector_id else utils.str_to_hash(str(vector))
        key = f'{namespace}:{vector_id}' if namespace else vector_id
        value = {
            "vector": vector,
            "metadata": meta
        }
        self.client.set(key, json.dumps(value))
        return vector_id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        key = f'{namespace}:{vector_id}' if namespace else vector_id
        result = self.client.get(key)
        if result:
            value = json.loads(result)
            return BaseVectorStoreDriver.Entry(
                id=vector_id,
                meta=value["metadata"],
                vector=value["vector"],
                namespace=namespace
            )
        else:
            return None

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        pattern = f'{namespace}:*' if namespace else '*'
        keys = self.client.keys(pattern)
        entries = []
        for key in keys:
            result = self.client.get(key)
            value = json.loads(result)
            entries.append(BaseVectorStoreDriver.Entry(
                id=key.decode().split(':')[-1],
                vector=value["vector"],
                meta=value["metadata"],
                namespace=namespace
            ))
        return entries

    def query(
            self,
            query: str, # change to match your specific query type
            count: Optional[int] = None,
            namespace: Optional[str] = None,
            include_vectors: bool = False,
            include_metadata: bool = True, # You can remove this if it's not needed
            **kwargs
    ) -> List[BaseVectorStoreDriver.QueryResult]:
        # Transform the query string into a query_vector suitable for Redis
        query_vector = self.embedding_driver.embed_string(query)
        params = {
            "vec": query_vector,
            "radius": 0.8 # or other logic to define the radius
        }

        query_expression = (
            Query("@vector:[VECTOR_RANGE $radius $vec]=>{$YIELD_DISTANCE_AS: score}")
            .sort_by("score")
            .return_fields("id", "score")
            .paging(0, count if count else 3)
            .dialect(2)
        )

        results = self.client.ft(self.INDEX_NAME).search(query_expression, params).docs

        return [
            BaseVectorStoreDriver.QueryResult(
                vector=document['id'],  # Change as needed
                score=document['score'],
                meta=None,  # Modify as needed
                namespace=None  # Modify as needed
            )
            for document in results
        ]
