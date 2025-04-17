from __future__ import annotations

import logging
from typing import TYPE_CHECKING, NoReturn, Optional

from attrs import Factory, define, field

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.drivers.embedding.dummy import DummyEmbeddingDriver
from griptape.drivers.vector import BaseVectorStoreDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    import sqlalchemy

    from griptape.drivers.embedding import BaseEmbeddingDriver

logger = logging.getLogger(__name__)


@define
class PgAiKnowledgeBaseVectorStoreDriver(BaseVectorStoreDriver):
    connection_string: str = field(kw_only=True, metadata={"serializable": True})
    knowledge_base_name: str = field(kw_only=True, metadata={"serializable": True})
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(lambda: DummyEmbeddingDriver()),
        metadata={"serializable": True},
        kw_only=True,
        init=False,
    )
    _engine: sqlalchemy.Engine = field(default=None, kw_only=True, alias="engine", metadata={"serializable": False})

    @lazy_property()
    def engine(self) -> sqlalchemy.Engine:
        return import_optional_dependency("sqlalchemy").create_engine(self.connection_string)

    def query(
        self,
        query: str | TextArtifact | ImageArtifact,
        *,
        count: Optional[int] = BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
        **kwargs,
    ) -> list[BaseVectorStoreDriver.Entry]:
        if isinstance(query, ImageArtifact):
            raise ValueError(f"{self.__class__.__name__} does not support querying with Image Artifacts.")

        sqlalchemy = import_optional_dependency("sqlalchemy")

        with sqlalchemy.orm.Session(self.engine) as session:
            rows = session.query(sqlalchemy.func.aidb.retrieve_text(self.knowledge_base_name, query, count)).all()

        entries = []
        for (row,) in rows:
            # Remove the first and last parentheses from the row and list by commas
            # Example: '(foo,bar)' -> ['foo', 'bar']
            row_list = "".join(row.replace("(", "", 1).rsplit(")", 1)).split(",")
            entries.append(
                BaseVectorStoreDriver.Entry(
                    id=row_list[0],
                    score=float(row_list[2]),
                    meta={"artifact": TextArtifact(row_list[1]).to_json()},
                )
            )

        return entries

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not support vector upsert.")

    def upsert_text_artifact(
        self,
        artifact: TextArtifact,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        vector_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not support text artifact upsert.")

    def upsert_text(
        self,
        string: str,
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs,
    ) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not support text upsert.")

    def load_entry(self, vector_id: str, *, namespace: Optional[str] = None) -> BaseVectorStoreDriver.Entry:
        raise NotImplementedError(f"{self.__class__.__name__} does not support entry loading.")

    def load_entries(self, *, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        raise NotImplementedError(f"{self.__class__.__name__} does not support entry loading.")

    def load_artifacts(self, *, namespace: Optional[str] = None) -> ListArtifact:
        raise NotImplementedError(f"{self.__class__.__name__} does not support Artifact loading.")

    def delete_vector(self, vector_id: str) -> NoReturn:
        raise NotImplementedError(f"{self.__class__.__name__} does not support deletion.")
