import uuid
from typing import Optional
from attr import define, field, Factory 
from griptape.drivers import BaseVectorStoreDriver
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, Column, String, JSON, select
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
    connection_string: str = field(kw_only=True)
    create_engine_params: Optional[dict] = field(factory=dict, kw_only=True)
    engine: Optional[Engine] = field(
        default=Factory(lambda self: create_engine(self.connection_string, **self.create_engine_params), takes_self=True)
    )

    Base = declarative_base()

    class Model(Base):
        __tablename__ = "griptape_vectors"

        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
        vector = Column(Vector())
        namespace = Column(String)
        meta = Column(JSON)

    def prepare_database(self) -> None:
        self.engine.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        self.engine.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

        self.Base.metadata.create_all(self.engine)

    def upsert_vector(
            self,
            vector: list[float],
            vector_id: Optional[str] = None,
            namespace: Optional[str] = None,
            meta: Optional[dict] = None,
            **kwargs
    ) -> str:
        with Session(self.engine) as session:
            obj = self.Model(
                id=vector_id,
                vector=vector,
                namespace=namespace,
                meta=meta,
            )

            obj = session.merge(obj)
            session.commit()

            return obj.id

    def load_entry(
            self,
            vector_id: str,
            namespace: Optional[str] = None
    ) -> BaseVectorStoreDriver.Entry:
        with Session(self.engine) as session:
            result = session.get(self.Model, vector_id)

            return BaseVectorStoreDriver.Entry(
                id=result.id,
                vector=result.vector,
                namespace=result.namespace,
                meta=result.meta,
            )

    def load_entries(self, namespace: Optional[str] = None) -> list[BaseVectorStoreDriver.Entry]:
        with Session(self.engine) as session:
            results = session.query(self.Model).filter_by(namespace=namespace).all()

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
        count = count if count else BaseVectorStoreDriver.DEFAULT_QUERY_COUNT
        vector = self.embedding_driver.embed_string(query)

        if distance_metric == "cosine_distance":
            op = self.Model.vector.cosine_distance(vector)
        elif distance_metric == "l2_distance":
            op = self.Model.vector.l2_distance(vector)
        elif distance_metric == "inner_product":
            op = self.Model.vector.max_inner_product(vector)
        else:
            raise ValueError("Invalid distance metric provided")

        with Session(self.engine) as session:
            query = session.query(
                self.Model,
                op.label("score")
            ).order_by(
                op
            )

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
