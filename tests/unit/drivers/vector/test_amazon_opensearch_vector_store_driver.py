from unittest.mock import Mock, create_autospec, patch

import boto3
import numpy as np
import pytest

from griptape.drivers import AmazonOpenSearchVectorStoreDriver


class TestAmazonOpenSearchVectorStoreDriver:
    @pytest.fixture()
    def driver(self):
        mock_session = create_autospec(boto3.Session, instance=True)
        mock_driver = create_autospec(AmazonOpenSearchVectorStoreDriver, instance=True, session=mock_session)
        mock_driver.upsert_vector.return_value = "foo"
        return mock_driver

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0.1, 0.2, 0.3], vector_id="foo", namespace="company") == "foo"

    def test_load_entry(self, driver):
        mock_entry = Mock()
        mock_entry.id = "foo2"
        mock_entry.vector = [2, 3, 4]
        mock_entry.meta = {"foo": "bar"}

        with patch.object(driver, "load_entry", return_value=mock_entry):
            entry = driver.load_entry("foo2", namespace="company")
            assert entry.id == "foo2"
            assert np.allclose(entry.vector, [2, 3, 4], atol=1e-6)
            assert entry.meta == {"foo": "bar"}

    def test_load_entries(self, driver):
        mock_entry = Mock()
        mock_entry.id = "try_load"
        mock_entry.vector = [0.7, 0.8, 0.9]
        mock_entry.meta = None

        with patch.object(driver, "load_entries", return_value=[mock_entry]):
            entries = driver.load_entries(namespace="company")
            assert len(entries) == 1
            assert entries[0].id == "try_load"
            assert np.allclose(entries[0].vector, [0.7, 0.8, 0.9], atol=1e-6)
            assert entries[0].meta is None

    def test_query(self, driver):
        mock_result = Mock()
        mock_result.id = "query_result"

        with patch.object(driver, "query", return_value=[mock_result]):
            query_vector = [0.5, 0.5, 0.5]
            results = driver.query(query_vector, count=5, namespace="company")
            assert len(results) == 1, "Expected results from the query"
            assert results[0].id == "query_result", "Expected a result id"
