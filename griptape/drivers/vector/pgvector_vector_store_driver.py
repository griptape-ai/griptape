import uuid
from typing import Optional
from attr import define, field, Factory
from dataclasses import dataclass
from griptape.drivers import BaseVectorStoreDriver
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector


@define
class PgVectorVectorStoreDriver(BaseVectorStoreDriver):
    """A vector store driver to Postgres using the PGVector extension.

    Attributes:
        connection_string: The connection string for the Postgres database instance.
        create_engine_params: Additional configuration params passed when creating the database connection.
        engine: An optional sqlalchemy Postgres engine to use.
    """

    connection_string: str = field(default=None, kw_only=True)
    create_engine_params: Optional[dict] = field(factory=dict, kw_only=True)
    _model: any = field(default=Factory(lambda self: self.vector_model_factory, takes_self=True), init=False)
    engine: Optional[Engine] = field(default=None, kw_only=True)

    def setup(
        self,
        table_name: str,
        create_schema: bool = True,
        install_uuid_extension: bool = True,
        install_vector_extension: bool = True,
        **kwargs
    ) -> None:
        """Provides a mechanism to initialize the database schema and extensions."""
        if self.engine is None and self.connection_string is None:
            raise ValueError("Either an engine or connection string must be provided")

        if self.engine is None:
            self.engine = create_engine(self.connection_string, **self.create_engine_params)

        self._model = self.vector_model_factory(table_name)

        if install_uuid_extension:
            self.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

        if install_vector_extension:
            self.engine.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

        if create_schema:
            self._model.metadata.create_all(self.engine)

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs
    ) -> str:
        """Inserts or updates a vector in the collection."""
        with Session(self.engine) as session:
            obj = self._model(
                id=vector_id,
                vector=vector,
                namespace=namespace,
                meta=meta,
            )

            obj = session.merge(obj)
            session.commit()

            return str(obj.id)

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> BaseVectorStoreDriver.Entry:
        """Retrieves a specific vector entry from the collection based on its identifier and optional namespace."""
        with Session(self.engine) as session:
            result = session.get(self._model, vector_id)

            return BaseVectorStoreDriver.Entry(
                id=result.id,
                vector=result.vector,
                namespace=result.namespace,
                meta=result.meta,
            )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        """Retrieves all vector entries from the collection, optionally filtering to only
        those that match the provided namespace.
        """
        with Session(self.engine) as session:
            query = session.query(self._model)
            if namespace:
                query = query.filter_by(namespace=namespace)

            results = query.all()

            return [
                BaseVectorStoreDriver.Entry(
                    id=str(result.id),
                    vector=result.vector,
                    namespace=result.namespace,
                    meta=result.meta,
                )
                for result in results
            ]

    def query(
        self,
        query: str,
        count: Optional[int] = BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        distance_metric: str = "cosine_distance",
        **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """Performs a search on the collection to find vectors similar to the provided input vector,
        optionally filtering to only those that match the provided namespace.
        """
        distance_metrics = {
            "cosine_distance": self._model.vector.cosine_distance,
            "l2_distance": self._model.vector.l2_distance,
            "inner_product": self._model.vector.max_inner_product,
        }

        if distance_metric not in distance_metrics:
            raise ValueError("Invalid distance metric provided")

        op = distance_metrics[distance_metric]

        with Session(self.engine) as session:
            vector = self.embedding_driver.embed_string(query)

            # The query should return both the vector and the distance metric score.
            query = session.query(
                self._model,
                op(vector).label("score"),
            ).order_by(op(vector))

            if namespace:
                query = query.filter_by(namespace=namespace)

            results = query.limit(count).all()

            return [
                BaseVectorStoreDriver.QueryResult(
                    vector=result[0].vector if include_vectors else None,
                    score=result[1],
                    meta=result[0].meta,
                    namespace=result[0].namespace,
                )
                for result in results
            ]

    @classmethod
    def vector_model_factory(cls, table_name: str) -> any:
        Base = declarative_base()

        @dataclass
        class VectorModel(Base):
            __tablename__ = table_name

            id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
            vector = Column(Vector())
            namespace = Column(String)
            meta = Column(JSON)

        return VectorModel
