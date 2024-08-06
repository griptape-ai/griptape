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
        logger.debug("rel_map: %s", rel_map)  # Debugging line to print the rel_map
        for k, v in rel_map.items():
            logger.debug("Key: %s, Value: %s", k, v)  # Debugging line to print keys and values in rel_map
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

    def test_refresh_ontology(self, driver, mock_client):
        mock_client.query.side_effect = [
            MagicMock(result_set=[["Property1"], ["Property2"]]),
            MagicMock(result_set=[["Relationship1"], ["Relationship2"]]),
        ]
        driver.refresh_ontology()
        ontology = driver.get_ontology(refresh=False)
        assert "Properties" in ontology
        assert "Relationships" in ontology
        mock_client.query.assert_called()
        logger.info("test_refresh_ontology passed")

    def test_get_ontology(self, driver, mock_client):
        mock_client.query.side_effect = [
            MagicMock(result_set=[["Property1"], ["Property2"]]),
            MagicMock(result_set=[["Relationship1"], ["Relationship2"]]),
        ]
        ontology = driver.get_ontology(refresh=True)
        assert "Properties" in ontology
        assert "Relationships" in ontology
        mock_client.query.assert_called()
        logger.info("test_get_ontology passed")

    def test_query(self, driver, mock_client):
        query = "MATCH (n) RETURN n LIMIT 1"
        mock_client.query.return_value.result_set = [["n"]]
        result = driver.query(query)
        assert result is not None
        mock_client.query.assert_any_call(query, params=None)
        logger.info("test_query passed")

    def test_load_entry(self, driver, mock_client):
        node_id = "test_node"
        properties = {"id": node_id, "name": "Test Node"}
        mock_client.query.return_value.result_set = [[MagicMock(properties=properties)]]
        entry = driver.load_entry(node_id)
        assert entry is not None
        assert entry.id == node_id
        assert entry.properties == properties
        mock_client.query.assert_called()
        logger.info("test_load_entry passed")

    def test_load_entries(self, driver, mock_client):
        properties1 = {"id": "node1", "name": "Node 1"}
        properties2 = {"id": "node2", "name": "Node 2"}
        mock_client.query.return_value.result_set = [
            MagicMock(properties=properties1),
            MagicMock(properties=properties2),
        ]
        entries = driver.load_entries()
        assert len(entries) == 2
        assert entries[0].properties == properties1
        assert entries[1].properties == properties2
        mock_client.query.assert_called()
        logger.info("test_load_entries passed")

    def test_upsert_node(self, driver, mock_client):
        node_data = {"id": "node1", "label": "Entity", "properties": {"name": "Node 1"}}
        driver.upsert_node(node_data)
        mock_client.query.assert_called()
        logger.info("test_upsert_node passed")
