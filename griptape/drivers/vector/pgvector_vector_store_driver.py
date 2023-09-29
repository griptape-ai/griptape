import uuid
from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseVectorStoreDriver
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector


@define
class PgVectorVectorStoreDriver(BaseVectorStoreDriver):
    """
    A vector store driver to Postgres using the PGVector extension.

    Attributes:
        connection_string: The connection string for the Postgres database instance.
        create_engine_params: Additional configuration params passed when creating the database connection.
        engine: An optional sqlalchemy Postgres engine to use.
    """

    connection_string: Optional[str] = field(default=None, kw_only=True)
    create_engine_params: Optional[dict] = field(factory=dict, kw_only=True)
    engine: Optional[Engine] = field(
        default=Factory(
            lambda self: create_engine(self.connection_string, **self.create_engine_params), takes_self=True
        )
    )

    class VectorModel(declarative_base()):
        __tablename__ = "griptape_vectors"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
        vector = Column(Vector())
        namespace = Column(String)
        meta = Column(JSON)

    def install_postgres_extensions(self) -> None:
        """
        Ensures the uuid-ossp and vector extensions are installed in the database.
        """
        self.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        self.engine.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

    def create_schema(self) -> None:
        """
        Creates the schema for the vectors table.
        """
        self.VectorModel.metadata.create_all(self.engine)

    def upsert_vector(
        self,
        vector: list[float],
        vector_id: Optional[str] = None,
        namespace: Optional[str] = None,
        meta: Optional[dict] = None,
        **kwargs
    ) -> str:
        """
        Inserts or updates a vector in the collection.
        """
        with Session(self.engine) as session:
            obj = self.VectorModel(
                id=vector_id,
                vector=vector,
                namespace=namespace,
                meta=meta,
            )

            obj = session.merge(obj)
            session.commit()

            return obj.id

    def load_entry(self, vector_id: str, namespace: Optional[str] = None) -> BaseVectorStoreDriver.Entry:
        """
        Retrieves a specific vector entry from the collection based on its identifier and optional namespace.
        """
        with Session(self.engine) as session:
            result = session.get(self.VectorModel, vector_id)

            return BaseVectorStoreDriver.Entry(
                id=result.id,
                vector=result.vector,
                namespace=result.namespace,
                meta=result.meta,
            )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        """
        Retrieves all vector entries from the collection, optionally filtering to only
        those that match the provided namespace.
        """
        with Session(self.engine) as session:
            query = session.query(self.VectorModel)
            if namespace:
                query = query.filter_by(namespace=namespace)

            results = query.all()

            return [
                BaseVectorStoreDriver.Entry(
                    id=result.id,
                    vector=result.vector,
                    namespace=result.namespace,
                    meta=result.meta,
                )
                for result in results
            ]

    def query(
        self,
        query: str,
        count: Optional[int] = None,
        namespace: Optional[str] = None,
        include_vectors: bool = False,
        distance_metric: str = "cosine_distance",
        **kwargs
    ) -> list[BaseVectorStoreDriver.QueryResult]:
        """
        Performs a search on the collection to find vectors similar to the provided input vector,
        optionally filtering to only those that match the provided namespace.
        """
        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT

        distance_metrics = {
            "cosine_distance": self.VectorModel.vector.cosine_distance,
            "l2_distance": self.VectorModel.vector.l2_distance,
            "inner_product": self.VectorModel.vector.max_inner_product,
        }
        op = distance_metrics[distance_metric]
        if op is None:
            raise ValueError("Invalid distance metric provided")

        with Session(self.engine) as session:
            vector = self.embedding_driver.embed_string(query)

            # The query should return both the vector and the distance metric score.
            query = session.query(
                self.VectorModel,
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
