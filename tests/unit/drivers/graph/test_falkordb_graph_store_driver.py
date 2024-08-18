from __future__ import annotations

import logging
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

from griptape.drivers.graph.base_graph_store_driver import BaseGraphStoreDriver
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
        logger.debug("rel_map: %s", rel_map)
        for k, v in rel_map.items():
            logger.debug("Key: %s, Value: %s", k, v)
        assert subj in rel_map
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


class TestBaseGraphStoreDriver:
    def test_base_graph_store_driver_init(self):
        class TestDriver(BaseGraphStoreDriver):
            def delete_node(self, node_id: str) -> None:
                pass

            def upsert_node(
                self, node_data: dict[str, Any], namespace: Optional[str] = None, meta: Optional[dict] = None, **kwargs
            ) -> str:
                pass

            def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[BaseGraphStoreDriver.Entry]:
                pass

            def load_entries(self, namespace: Optional[str] = None) -> list[BaseGraphStoreDriver.Entry]:
                pass

            def query(
                self, query: str, params: Optional[dict[str, Any]] = None, namespace: Optional[str] = None, **kwargs
            ) -> Any:
                pass

        driver = TestDriver()
        assert driver is not None

    def test_upsert_artifacts(self, mocker):
        class TestDriver(BaseGraphStoreDriver):
            def delete_node(self, node_id: str) -> None:
                pass

            def upsert_node(
                self, node_data: dict[str, Any], namespace: Optional[str] = None, meta: Optional[dict] = None, **kwargs
            ) -> str:
                pass

            def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[BaseGraphStoreDriver.Entry]:
                pass

            def load_entries(self, namespace: Optional[str] = None) -> list[BaseGraphStoreDriver.Entry]:
                pass

            def query(
                self, query: str, params: Optional[dict[str, Any]] = None, namespace: Optional[str] = None, **kwargs
            ) -> Any:
                pass

        driver = TestDriver()

        # Mock the BaseArtifact object with the expected methods
        mock_artifact = MagicMock()
        mock_artifact.to_json.return_value = '{"artifact": "json"}'
        mock_artifact.to_text.return_value = "text"

        artifacts = {"namespace1": [mock_artifact, mock_artifact], "namespace2": [mock_artifact]}

        mocker.patch.object(driver, "upsert_artifact", return_value="node_id")
        driver.upsert_artifacts(artifacts)
        logger.info("test_upsert_artifacts passed")

    def test_upsert_artifact_exists(self, mocker):
        class TestDriver(BaseGraphStoreDriver):
            def delete_node(self, node_id: str) -> None:
                pass

            def upsert_node(
                self, node_data: dict[str, Any], namespace: Optional[str] = None, meta: Optional[dict] = None, **kwargs
            ) -> str:
                pass

            def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[BaseGraphStoreDriver.Entry]:
                pass

            def load_entries(self, namespace: Optional[str] = None) -> list[BaseGraphStoreDriver.Entry]:
                pass

            def query(
                self, query: str, params: Optional[dict[str, Any]] = None, namespace: Optional[str] = None, **kwargs
            ) -> Any:
                pass

        driver = TestDriver()

        # Mock the BaseArtifact object
        mock_artifact = MagicMock()
        mock_artifact.to_json.return_value = '{"artifact": "json"}'
        mock_artifact.to_text.return_value = "text"

        mocker.patch.object(driver, "does_entry_exist", return_value=True)
        node_id = driver.upsert_artifact(mock_artifact, namespace="namespace1")
        assert node_id is not None
        logger.info("test_upsert_artifact_exists passed")

    def test_upsert_artifact_new(self, mocker):
        class TestDriver(BaseGraphStoreDriver):
            def delete_node(self, node_id: str) -> None:
                pass

            def upsert_node(
                self, node_data: dict[str, Any], namespace: Optional[str] = None, meta: Optional[dict] = None, **kwargs
            ) -> str:
                pass

            def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[BaseGraphStoreDriver.Entry]:
                pass

            def load_entries(self, namespace: Optional[str] = None) -> list[BaseGraphStoreDriver.Entry]:
                pass

            def query(
                self, query: str, params: Optional[dict[str, Any]] = None, namespace: Optional[str] = None, **kwargs
            ) -> Any:
                pass

        driver = TestDriver()

        # Mock the BaseArtifact object
        mock_artifact = MagicMock()
        mock_artifact.to_json.return_value = '{"artifact": "json"}'
        mock_artifact.to_text.return_value = "text"

        mocker.patch.object(driver, "does_entry_exist", return_value=False)
        mocker.patch.object(driver, "upsert_node", return_value="new_node_id")
        node_id = driver.upsert_artifact(mock_artifact, namespace="namespace1")
        assert node_id == "new_node_id"
        logger.info("test_upsert_artifact_new passed")

    def test_does_entry_exist(self, mocker):
        class TestDriver(BaseGraphStoreDriver):
            def delete_node(self, node_id: str) -> None:
                pass

            def upsert_node(
                self, node_data: dict[str, Any], namespace: Optional[str] = None, meta: Optional[dict] = None, **kwargs
            ) -> str:
                pass

            def load_entry(self, node_id: str, namespace: Optional[str] = None) -> Optional[BaseGraphStoreDriver.Entry]:
                pass

            def load_entries(self, namespace: Optional[str] = None) -> list[BaseGraphStoreDriver.Entry]:
                pass

            def query(
                self, query: str, params: Optional[dict[str, Any]] = None, namespace: Optional[str] = None, **kwargs
            ) -> Any:
                pass

        driver = TestDriver()
        mocker.patch.object(driver, "load_entry", return_value=None)
        exists = driver.does_entry_exist("test_id", "namespace1")
        assert not exists
        logger.info("test_does_entry_exist passed")
