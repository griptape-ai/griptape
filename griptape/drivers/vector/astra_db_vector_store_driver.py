from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import BaseVectorStoreDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from astrapy import Collection

GRIPTAPE_VERSION: Optional[str]
try:
    from importlib import metadata

    GRIPTAPE_VERSION = metadata.version("griptape")
except Exception:
    GRIPTAPE_VERSION = None

logging.basicConfig(level=logging.WARNING)


COLLECTION_INDEXING = {"deny": ["meta.artifact"]}


@define
class AstraDBVectorStoreDriver(BaseVectorStoreDriver):
    """A Vector Store Driver for Astra DB.

    DOCSTRING TO DO
    """

    api_endpoint: str = field(kw_only=True, metadata={"serializable": True})
    token: str = field(kw_only=True, metadata={"serializable": False})
    collection_name: str = field(kw_only=True, metadata={"serializable": False})
    dimension: int = field(kw_only=True, metadata={"serializable": True})
    astra_db_namespace: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    collection: Collection = field(init=False)

    def __attrs_post_init__(self) -> None:
        astrapy = import_optional_dependency("astrapy")
        self.collection = (
            astrapy.DataAPIClient(
                token=self.token,
                caller_name="griptape",
                caller_version=GRIPTAPE_VERSION,
            )
            .get_database(
                self.api_endpoint,
                namespace=self.astra_db_namespace,
            )
            .create_collection(
                name=self.collection_name,
                dimension=self.dimension,
                indexing=COLLECTION_INDEXING,
                check_exists=False,
            )
        )

    def delete_vector(self, vector_id: str) -> None:
        self.collection.delete_one({"_id": vector_id})

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        document = {
            k: v
            for k, v in {"$vector": vector, "_id": vector_id, "namespace": namespace, "meta": meta}.items()
            if v is not None
        }
        if vector_id is not None:
            self.collection.find_one_and_replace({"_id": vector_id}, document, upsert=True)
            return vector_id
        else:
            insert_result = self.collection.insert_one(document)
            return insert_result.inserted_id

    def load_entry(self, vector_id: str, *, namespace: Optional[str] = None) -> Optional[BaseVectorStoreDriver.Entry]:
        find_filter = {k: v for k, v in {"_id": vector_id, "namespace": namespace}.items() if v is not None}
        match = self.collection.find_one(find_filter, projection={"*": 1})
        if match:
            return BaseVectorStoreDriver.Entry(
                id=match["_id"], vector=match.get("$vector"), meta=match.get("meta"), namespace=match.get("namespace")
            )
        else:
            return None

    def load_entries(self, *, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        find_filter: dict[str, str] = {} if namespace is None else {"namespace": namespace}
        return [
            BaseVectorStoreDriver.Entry(
                id=match["_id"], vector=match.get("$vector"), meta=match.get("meta"), namespace=match.get("namespace")
            )
            for match in self.collection.find(filter=find_filter, projection={"*": 1})
        ]

    def query(
        self,
        query: str,
        *,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        **kwargs: Any,
    ) -> list[BaseVectorStoreDriver.Entry]:
        query_filter: Optional[dict[str, Any]] = kwargs.pop("filter", None)
        if kwargs:
            warnings.warn(
                "Unhandled keyword argument(s) provided to AstraDBVectorStore.query: "
                f"'{','.join(sorted(kwargs.keys()))}'. These will be ignored.",
                stacklevel=2,
            )
        find_filter_ns: dict[str, Any] = {} if namespace is None else {"namespace": namespace}
        find_filter = {**(query_filter or {}), **find_filter_ns}
        find_projection: Optional[dict[str, int]] = {"*": 1} if include_vectors else None
        vector = self.embedding_driver.embed_string(query)
        matches = self.collection.find(
            filter=find_filter,
            sort={"$vector": vector},
            limit=count,
            projection=find_projection,
            include_similarity=True,
        )
        return [
            BaseVectorStoreDriver.Entry(
                id=match["_id"],
                vector=match.get("$vector"),
                score=match["$similarity"],
                meta=match.get("meta"),
                namespace=match.get("namespace"),
            )
            for match in matches
        ]
