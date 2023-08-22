import pytest
from griptape.drivers import OpenSearchVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
import numpy as np


class TestOpenSearchVectorStoreDriver:

    @pytest.fixture(scope="module")
    def driver(self):
        # Make sure OpenSearch is configured correctly for these tests
        return OpenSearchVectorStoreDriver(
            host='your-open-search-endpoint.amazonaws.com',
            aws_access_key='YOUR_AWS_ACCESS_KEY',
            aws_secret_key='YOUR_AWS_SECRET_KEY',
            region='us-east-1',
            index_name='test_index',
            embedding_driver=MockEmbeddingDriver()
        )

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0.1, 0.2, 0.3], vector_id="foo", namespace="company") == "foo"

    def test_load_entry(self, driver):
        entry_id = "foo2"
        vector = [2, 3, 4]
        metadata = {"foo": "bar"}
        driver.upsert_vector(vector, entry_id, namespace="company", meta=metadata)

        entry = driver.load_entry(entry_id, namespace="company")
        assert entry.id == entry_id
        assert np.allclose(entry.vector, vector, atol=1e-6)
        assert entry.meta == metadata

    def test_load_entries(self, driver):
        driver.upsert_vector([0.7, 0.8, 0.9], vector_id="try_load", namespace="company")

        entries = driver.load_entries(namespace="company")
        assert len(entries) > 0
        assert any(entry.id == "try_load" for entry in entries)
        assert any(np.allclose(entry.vector, [0.7, 0.8, 0.9], atol=1e-6) for entry in entries)
        assert any(entry.meta is None for entry in entries)

    def test_query(self, driver):
        # Assuming the query function for OpenSearchVectorStoreDriver takes in a query string
        query_string = "test"
        results = driver.query(query_string, count=5, namespace="company")

        # You might have to adjust the below assertion depending on your OpenSearch query logic
        assert len(results) > 0, "Expected results from the query"
