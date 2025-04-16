from unittest.mock import MagicMock

import json
import pytest

from griptape.drivers.vector.pgai import PGAIKnowledgeBaseVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestPGAIKnowledgeBaseVectorVectorStoreDriver:
    connection_string = "postgresql://postgres:postgres@localhost:5432/postgres"
    knowledge_base_name = "example_knowledge_base"

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

    def test_initialize(self, embedding_driver):
        PGAIKnowledgeBaseVectorStoreDriver(
            connection_string=self.connection_string, knowledge_base_name=self.knowledge_base_name
        )

    def test_query(self, mock_engine):
        test_ids = [17, 23]
        test_values = ["foo", "bar"]
        test_scores = [0.4, 0.6]
        test_result = [
            [test_ids[0], test_values[0], test_scores[0]],
            [test_ids[1], test_values[1], test_scores[1]],
        ]
        mock_engine.begin.return_value.__enter__.return_value.execute.return_value = test_result

        driver = PGAIKnowledgeBaseVectorStoreDriver(
            engine=mock_engine, connection_string=self.connection_string, knowledge_base_name=self.knowledge_base_name
        )

        result = driver.query("some query")

        assert result[0].id == str(test_ids[0])
        assert result[1].id == str(test_ids[1])
        assert result[0].meta
        assert json.loads(result[0].meta["artifact"])["value"] == test_values[0]
        assert result[1].meta
        assert json.loads(result[1].meta["artifact"])["value"] == test_values[1]
        assert result[0].score == test_scores[0]
        assert result[1].score == test_scores[1]
