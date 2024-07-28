from unittest.mock import MagicMock

import pytest

from griptape.drivers import AstraDBVectorStoreDriver, BaseVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

one_document = {
    "_id": "doc_id",
    "$vector": [3.0, 2.0, 1.0],
    "meta": "doc_meta",
    "namespace": "doc_namespace",
    "$similarity": 10,
}
one_entry = BaseVectorStoreDriver.Entry(
    id=one_document["_id"],
    vector=one_document["$vector"],
    meta=one_document["meta"],
    namespace=one_document["namespace"],
)
one_query_entry = BaseVectorStoreDriver.Entry(
    id=one_document["_id"],
    vector=one_document["$vector"],
    meta=one_document["meta"],
    namespace=one_document["namespace"],
    score=one_document["$similarity"],
)


class TestAstraDBVectorStoreDriver:
    @pytest.fixture(autouse=True)
    def base_mock_collection(self, mocker):
        mock_create_collection = mocker.patch(
            "astrapy.DataAPIClient"
        ).return_value.get_database.return_value.create_collection
        return mock_create_collection

    @pytest.fixture()
    def mock_collection(self, base_mock_collection):
        """Augmented with specific response to certain method calls."""
        # insert_one with server-side provided ID
        mock_insert_one_return_value = MagicMock()
        mock_insert_one_return_value.inserted_id = "insert_one_server_side_id"
        base_mock_collection.return_value.insert_one.return_value = mock_insert_one_return_value
        # find_one
        base_mock_collection.return_value.find_one.return_value = one_document
        # find
        base_mock_collection.return_value.find.return_value = [one_document]
        #
        return base_mock_collection

    @pytest.fixture()
    def mock_collection_findnothing(self, base_mock_collection):
        """`find` and `find_one` return nothing."""
        base_mock_collection.return_value.find_one.return_value = None
        base_mock_collection.return_value.find.return_value = []
        return base_mock_collection

    @pytest.fixture()
    def driver(self, mock_collection):
        return AstraDBVectorStoreDriver(
            api_endpoint="ep",
            token="to",
            collection_name="co",
            astra_db_namespace="ns",
            embedding_driver=MockEmbeddingDriver(dimensions=3),
        )

    def test_explicit_dimension(self, mock_collection):
        AstraDBVectorStoreDriver(
            api_endpoint="ep",
            token="to",
            collection_name="co",
            astra_db_namespace="ns",
            dimension=123,
            embedding_driver=MockEmbeddingDriver(),
        )

    def test_delete_vector(self, driver, mock_collection):
        driver.delete_vector("deletee_id")
        mock_collection.return_value.delete_one.assert_called_once()

    def test_upsert_vector_with_id(self, driver, mock_collection):
        upserted_id = driver.upsert_vector([1.0, 2.0, 3.0], vector_id="some_vector_id", namespace="some_namespace")
        assert upserted_id == "some_vector_id"
        mock_collection.return_value.find_one_and_replace.assert_called_once()

    def test_upsert_vector_kwargs_warning(self, driver, mock_collection):
        with pytest.warns(UserWarning):
            upserted_id = driver.upsert_vector(
                [1.0, 2.0, 3.0], vector_id="some_vector_id", namespace="some_namespace", kittens=123, marzipan="yes"
            )
        assert upserted_id == "some_vector_id"
        mock_collection.return_value.find_one_and_replace.assert_called_once()

    def test_upsert_vector_no_id(self, driver, mock_collection):
        upserted_id = driver.upsert_vector([1.0, 2.0, 3.0], namespace="some_namespace")
        assert upserted_id == "insert_one_server_side_id"
        mock_collection.return_value.insert_one.assert_called_once()

    def test_load_entry(self, driver, mock_collection):
        entry = driver.load_entry("vector_id", namespace="some_namespace")
        assert entry == one_entry
        mock_collection.return_value.find_one.assert_called_once_with(
            filter={"_id": "vector_id", "namespace": "some_namespace"},
            projection={"*": 1},
        )

    def test_load_entry_empty(self, driver, mock_collection_findnothing):
        entry = driver.load_entry("vector_id", namespace="some_namespace")
        assert entry is None
        mock_collection_findnothing.return_value.find_one.assert_called_once_with(
            filter={"_id": "vector_id", "namespace": "some_namespace"},
            projection={"*": 1},
        )

    def test_load_entries(self, driver, mock_collection):
        entries = driver.load_entries(namespace="some_namespace")
        assert entries == [one_entry]
        mock_collection.return_value.find.assert_called_once_with(
            filter={"namespace": "some_namespace"},
            projection={"*": 1},
        )

    def test_query_allparams(self, driver, mock_collection):
        entries1 = driver.query("some query", count=999, namespace="some_namespace", include_vectors=True)
        assert entries1 == [one_query_entry]
        query_vector = driver.embedding_driver.embed_string("some query")
        mock_collection.return_value.find.assert_called_once_with(
            filter={"namespace": "some_namespace"},
            sort={"$vector": query_vector},
            limit=999,
            projection={"*": 1},
            include_similarity=True,
        )

    def test_query_minparams(self, driver, mock_collection):
        entries0 = driver.query("some query")
        assert entries0 == [one_query_entry]
        query_vector = driver.embedding_driver.embed_string("some query")
        mock_collection.return_value.find.assert_called_once_with(
            filter={},
            sort={"$vector": query_vector},
            limit=BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
            projection=None,
            include_similarity=True,
        )

    def test_query_kwargs_warning(self, driver, mock_collection):
        with pytest.warns(UserWarning):
            entries0 = driver.query("some query", sector=987, voltage="12 V")
        assert entries0 == [one_query_entry]
        query_vector = driver.embedding_driver.embed_string("some query")
        mock_collection.return_value.find.assert_called_once_with(
            filter={},
            sort={"$vector": query_vector},
            limit=BaseVectorStoreDriver.DEFAULT_QUERY_COUNT,
            projection=None,
            include_similarity=True,
        )
