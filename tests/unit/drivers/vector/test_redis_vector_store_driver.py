import pytest
from griptape.drivers import RedisVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
import numpy as np


class TestRedisVectorStoreDriver:
    @pytest.fixture(scope="module")
    def driver(self):
        # Make sure the Redis server is running with this configuration
        return RedisVectorStoreDriver(
            host='redis-12146.c10.us-east-1-2.ec2.cloud.redislabs.com',  # Replace with your host
            port=12146,  # Replace with your port (e.g., 6379)
            password='SmilingatGriptape',  # Replace with your password if required
            db=0,
            index='idx1',
            embedding_driver=MockEmbeddingDriver(),  # Replace with the actual embedding driver if needed
        )

    def test_upsert_vector(self, driver):
        assert driver.upsert_vector([0.1, 0.2, 0.3], vector_id="foo") == "foo"

    def test_load_entry(self, driver):
        # Insert the expected entry into Redis using the upsert method
        entry_id = "foo2"
        vector = [2, 3, 4]
        metadata = {"foo": "bar"}
        driver.upsert_vector(vector, entry_id, None, metadata)

        entry = driver.load_entry("foo2")
        assert entry.id == "foo2"
        assert entry.vector == [2, 3, 4]
        assert entry.meta == {"foo": "bar"}  # This should now pass

    def test_load_entries(self, driver):
        # Inserting some data to ensure consistent testing
        driver.upsert_vector([0.7, 0.8, 0.9], vector_id="try_load")

        entries = driver.load_entries()
        assert len(entries) > 0
        assert any(entry.id == "try_load" for entry in entries)
        assert any(np.allclose(entry.vector, [0.7, 0.8, 0.9], atol=1e-6) for entry in entries)
        assert any(entry.meta is None for entry in entries)

    import numpy as np

    def test_query(self, driver):
        vector_id = "query_test"
        vector = [0.1, 0.2, 0.3]
        driver.upsert_vector(vector, vector_id)
        results = driver.query(vector_id, count=5)

        found_vector = any(np.allclose(result.vector, vector, atol=1e-6) for result in results)
        print("Results:", [result.vector for result in results])
        print("Expected:", vector)
        assert found_vector, "Expected vector not found in results"

