import pytest

from griptape.drivers.vector.dummy import DummyVectorStoreDriver
from griptape.exceptions import DummyError


class TestDummyVectorStoreDriver:
    @pytest.fixture()
    def vector_store_driver(self):
        return DummyVectorStoreDriver()

    def test_delete_vector(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.delete_vector("foo bar huzzah")

    def test_upsert_vector(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.upsert_vector("foo bar huzzah")

    def test_load_entry(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.load_entry("foo bar huzzah")

    def test_load_entries(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.load_entries(namespace="foo bar huzzah")

    def test_query_vector(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.query_vector([0.0, 0.5])

    def test_query(self, vector_store_driver):
        with pytest.raises(DummyError):
            vector_store_driver.query("foo bar huzzah")
