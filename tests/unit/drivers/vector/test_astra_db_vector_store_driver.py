from unittest.mock import MagicMock

import pytest

from griptape.drivers import AstraDBVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestAstraDBVectorStoreDriver:
    @pytest.fixture(autouse=True)
    def mock_collection(self, mocker):
        mock_create_collection = mocker.patch(
            "astrapy.DataAPIClient"
        ).return_value.get_database.return_value.create_collection
        return mock_create_collection

    @pytest.fixture()
    def autoid_mock_collection(self, mock_collection):
        mock_insert_one_return_value = MagicMock()
        mock_insert_one_return_value.inserted_id = "server_side_id"
        mock_collection.return_value.insert_one.return_value = mock_insert_one_return_value
        return mock_collection

    @pytest.fixture()
    def driver(self, autoid_mock_collection):
        return AstraDBVectorStoreDriver(
            api_endpoint="ep",
            token="to",
            collection_name="co",
            dimension=3,
            astra_db_namespace="ns",
            embedding_driver=MockEmbeddingDriver(dimensions=3),
        )

    def test_upsert_vector_with_id(self, driver):
        upserted_id = driver.upsert_vector([1.0, 2.0, 3.0], vector_id="some_vector_id", namespace="some_namespace")
        assert upserted_id == "some_vector_id"

    def test_upsert_vector_no_id(self, driver):
        upserted_id = driver.upsert_vector([1.0, 2.0, 3.0], namespace="some_namespace")
        assert upserted_id == "server_side_id"
