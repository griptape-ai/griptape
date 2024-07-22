import logging
from unittest.mock import MagicMock

import pytest

from griptape.drivers.graph.falkordb_graph_store_driver import FalkorDBGraphStoreDriver

logger = logging.getLogger(__name__)


class TestFalkorDBGraphStoreDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("falkordb.FalkorDB.from_url").return_value.select_graph.return_value
        mock_client.query.return_value = MagicMock(result_set=[[1]])
        return mock_client

    @pytest.fixture()
    def driver(self, mock_client):
        url = "redis://localhost:6379"
        database = "falkor"
        node_label = "Entity"
        return FalkorDBGraphStoreDriver(url=url, database=database, node_label=node_label)

    def test_connect(self, driver):
        assert driver.client is not None
        logger.info("test_connect passed")

    def test_upsert_triplet(self, driver, mock_client):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        driver.upsert_triplet(subj, rel, obj)
        mock_client.query.assert_called()
        logger.info("test_upsert_triplet passed")

    def test_get_triplets(self, driver, mock_client):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        mock_client.query.return_value.result_set = [[rel, obj]]
        triplets = driver.get(subj)
        assert len(triplets) == 1
        assert triplets[0][1] == obj
        mock_client.query.assert_called()
        logger.info("test_get_triplets passed")

    def test_get_rel_map(self, driver, mock_client):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        mock_client.query.return_value.result_set = [
            [
                MagicMock(
                    nodes=lambda: [MagicMock(properties={"id": subj}), MagicMock(properties={"id": obj})],
                    edges=lambda: [MagicMock(relation=rel)],
                )
            ]
        ]
        subjs = [subj]
        rel_map = driver.get_rel_map(subjs=subjs)
        logger.debug(f"rel_map: {rel_map}")  # Debugging line to print the rel_map
        for k, v in rel_map.items():
            logger.debug(f"Key: {k}, Value: {v}")  # Debugging line to print keys and values in rel_map
        assert subj in rel_map  # Ensure the key exists
        assert rel_map[subj] == [[rel, obj]]
        mock_client.query.assert_called()
        logger.info("test_get_rel_map passed")

    def test_delete_triplet(self, driver, mock_client):
        subj = "test_subject"
        rel = "test_relation"
        obj = "test_object"
        driver.upsert_triplet(subj, rel, obj)
        driver.delete(subj, rel, obj)
        mock_client.query.return_value.result_set = []
        triplets = driver.get(subj)
        assert not any(obj in triplet for triplet in triplets)
        mock_client.query.assert_called()
        logger.info("test_delete_triplet passed")

    def test_refresh_schema(self, driver, mock_client):
        mock_client.query.side_effect = [
            MagicMock(result_set=[["Property1"], ["Property2"]]),
            MagicMock(result_set=[["Relationship1"], ["Relationship2"]]),
        ]
        driver.refresh_schema()
        assert "Properties" in driver.schema
        assert "Relationships" in driver.schema
        mock_client.query.assert_called()
        logger.info("test_refresh_schema passed")

    def test_get_schema(self, driver, mock_client):
        mock_client.query.side_effect = [
            MagicMock(result_set=[["Property1"], ["Property2"]]),
            MagicMock(result_set=[["Relationship1"], ["Relationship2"]]),
        ]
        schema = driver.get_schema(refresh=True)
        assert "Properties" in schema
        assert "Relationships" in schema
        mock_client.query.assert_called()
        logger.info("test_get_schema passed")

    def test_query(self, driver, mock_client):
        query = "MATCH (n) RETURN n LIMIT 1"
        mock_client.query.return_value.result_set = [["n"]]
        result = driver.query(query)
        assert result is not None
        mock_client.query.assert_any_call(query, params=None)
        logger.info("test_query passed")
