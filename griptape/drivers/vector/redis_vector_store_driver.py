from typing import Optional
from griptape import utils
from griptape.drivers import BaseVectorStoreDriver
import redis
from attr import define, field
import json


@define
class RedisVectorStoreDriver(BaseVectorStoreDriver):
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

    def query(self, query: str, count: Optional[int] = None, namespace: Optional[str] = None,
              include_vectors: bool = False, **kwargs) -> list[BaseVectorStoreDriver.QueryResult]:
        raise NotImplementedError("Vector similarity queries are not directly supported by Redis.")

    def create_index(self, name: str, **kwargs) -> None:
        pass
