from attrs import field, define, Factory
from typing import Optional
from griptape.drivers import BaseVectorStoreDriver, BaseEmbeddingDriver, DummyEmbeddingDriver
from griptape.exceptions import DummyException


@define()
class DummyVectorStoreDriver(BaseVectorStoreDriver):
    embedding_driver: BaseEmbeddingDriver = field(
        kw_only=True, default=Factory(lambda: DummyEmbeddingDriver()), metadata={"serializable": True}
    )

    def delete_vector(self, vector_id: str) -> None:
        raise DummyException(__class__.__name__, "delete_vector")

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        raise DummyException(__class__.__name__, "upsert_vector")

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        raise DummyException(__class__.__name__, "load_entry")

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        raise DummyException(__class__.__name__, "load_entries")

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        raise DummyException(__class__.__name__, "query")
