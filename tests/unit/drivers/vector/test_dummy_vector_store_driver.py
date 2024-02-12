import pytest
from griptape.drivers import DummyVectorStoreDriver
from griptape.exceptions import DummyException


class TestDummyVectorStoreDriver:
    @pytest.fixture
    def vector_store_driver(self):
        return DummyVectorStoreDriver()

    def test_delete_vector(self, vector_store_driver):
        with pytest.raises(DummyException):
            vector_store_driver.delete_vector("foo bar huzzah")

    def test_upsert_vector(self, vector_store_driver):
        with pytest.raises(DummyException):
            vector_store_driver.upsert_vector("foo bar huzzah")

    def test_load_entry(self, vector_store_driver):
        with pytest.raises(DummyException):
            vector_store_driver.load_entry("foo bar huzzah")

    def test_load_entries(self, vector_store_driver):
        with pytest.raises(DummyException):
            vector_store_driver.load_entries("foo bar huzzah")

    def test_query(self, vector_store_driver):
        with pytest.raises(DummyException):
            vector_store_driver.query("foo bar huzzah")
