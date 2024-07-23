import uuid
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from sqlalchemy import create_engine

from griptape.drivers import PgVectorVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestPgVectorVectorStoreDriver:
    connection_string = "postgresql://postgres:postgres@localhost:5432/postgres"
    table_name = "griptape_vectors"

    @pytest.fixture()
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture()
    def mock_engine(self):
        return MagicMock()

    @pytest.fixture()
    def mock_session(self, mocker):
        session = MagicMock()
        mock_session_manager = MagicMock()
        mock_session_manager.__enter__.return_value = session
        mocker.patch("sqlalchemy.orm.Session", return_value=mock_session_manager)

        return session

    def test_initialize_requires_engine_or_connection_string(self, embedding_driver):
        with pytest.raises(ValueError):
            PgVectorVectorStoreDriver(embedding_driver=embedding_driver, table_name=self.table_name)

    def test_initialize_accepts_engine(self, embedding_driver):
        engine: Any = create_engine(self.connection_string)
        PgVectorVectorStoreDriver(embedding_driver=embedding_driver, engine=engine, table_name=self.table_name)

    def test_initialize_accepts_connection_string(self, embedding_driver):
        PgVectorVectorStoreDriver(
            embedding_driver=embedding_driver, connection_string=self.connection_string, table_name=self.table_name
        )

    def test_upsert_vector(self, mock_session, mock_engine):
        test_id = str(uuid.uuid4())
        mock_session.merge.return_value = Mock(id=test_id)

        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        returned_id = driver.upsert_vector([1.0, 2.0, 3.0])

        assert returned_id == test_id
        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_load_entry(self, mock_session, mock_engine):
        test_id = str(uuid.uuid4())
        test_vec = [0.1, 0.2, 0.3]
        test_namespace = str(uuid.uuid4())
        test_meta = {"key": "value"}
        mock_session.get.return_value = Mock(id=test_id, vector=test_vec, namespace=test_namespace, meta=test_meta)

        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        entry = driver.load_entry(vector_id=test_id)

        assert entry.id == test_id
        assert entry.vector == test_vec
        assert entry.namespace == test_namespace
        assert entry.meta == test_meta

    def test_load_entries(self, mock_session, mock_engine):
        test_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_vecs = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        test_namespaces = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_metas = [{"key": "value1"}, {"key": "value2"}]
        mock_query = MagicMock()
        mock_query.all.return_value = [
            Mock(id=test_ids[0], vector=test_vecs[0], namespace=test_namespaces[0], meta=test_metas[0]),
            Mock(id=test_ids[1], vector=test_vecs[1], namespace=test_namespaces[1], meta=test_metas[1]),
        ]
        mock_session.query.return_value = mock_query

        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        entries = driver.load_entries()

        assert entries[0].id == test_ids[0]
        assert entries[1].id == test_ids[1]
        assert entries[0].vector == test_vecs[0]
        assert entries[1].vector == test_vecs[1]
        assert entries[0].namespace == test_namespaces[0]
        assert entries[1].namespace == test_namespaces[1]
        assert entries[0].meta == test_metas[0]
        assert entries[1].meta == test_metas[1]

    def test_query_invalid_distance_metric(self, mock_engine):
        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        with pytest.raises(ValueError):
            driver.query("test", distance_metric="invalid")

    def test_query(self, mock_session, mock_engine):
        test_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_vecs = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        test_namespaces = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_metas = [{"key": "value1"}, {"key": "value2"}]
        test_result = [
            [Mock(id=test_ids[0], vector=test_vecs[0], namespace=test_namespaces[0], meta=test_metas[0]), 0.1],
            [Mock(id=test_ids[1], vector=test_vecs[1], namespace=test_namespaces[1], meta=test_metas[1]), 0.9],
        ]
        mock_session.query().order_by().limit().all.return_value = test_result

        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        result = driver.query("some query", include_vectors=True)

        assert result[0].id == test_ids[0]
        assert result[1].id == test_ids[1]
        assert result[0].vector == test_vecs[0]
        assert result[1].vector == test_vecs[1]
        assert result[0].namespace == test_namespaces[0]
        assert result[1].namespace == test_namespaces[1]
        assert result[0].meta == test_metas[0]
        assert result[1].meta == test_metas[1]

    def test_query_filter(self, mock_session, mock_engine):
        test_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_vecs = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        test_namespaces = [str(uuid.uuid4()), str(uuid.uuid4())]
        test_metas = [{"key": "value1"}, {"key": "value2"}]
        test_result = [
            [Mock(id=test_ids[0], vector=test_vecs[0], namespace=test_namespaces[0], meta=test_metas[0]), 0.1]
        ]
        mock_session.query().order_by().filter_by().limit().all.return_value = test_result

        driver = PgVectorVectorStoreDriver(
            embedding_driver=MockEmbeddingDriver(), engine=mock_engine, table_name=self.table_name
        )

        result = driver.query("some query", include_vectors=True, filter={"namespace": test_namespaces[0]})

        assert result[0].id == test_ids[0]
        assert result[0].vector == test_vecs[0]
        assert result[0].namespace == test_namespaces[0]
        assert result[0].meta == test_metas[0]
