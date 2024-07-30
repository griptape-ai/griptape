from __future__ import annotations

import json
import math
import os

import pytest

from griptape.drivers import AstraDbVectorStoreDriver, BaseVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

TEST_COLLECTION_NAME = "gt_int_test"
TEST_COLLECTION_NAME_METRIC = "gt_int_test_dot"


class TestAstraDbVectorStoreDriver:
    @pytest.fixture()
    def embedding_driver(self):
        def circle_fraction_string_to_vector(chunk: str) -> list[float]:
            try:
                fraction = float(json.loads(chunk))
                angle = fraction * math.pi * 2
                return [math.cos(angle), math.sin(angle)]
            except Exception:
                return [0.0, 0.0]

        return MockEmbeddingDriver(mock_output=circle_fraction_string_to_vector)

    @pytest.fixture()
    def vector_store_collection(self):
        import astrapy

        database = astrapy.DataAPIClient().get_database(
            api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
            token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
            namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
        )
        collection = database.create_collection(
            name=TEST_COLLECTION_NAME,
            dimension=2,
            metric="cosine",
        )
        yield collection
        collection.drop()

    @pytest.fixture()
    def vector_store_driver(self, embedding_driver, vector_store_collection):
        driver = AstraDbVectorStoreDriver(
            api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
            token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
            collection_name=vector_store_collection.name,
            astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
            embedding_driver=embedding_driver,
        )
        return driver

    def test_vector_crud(self, vector_store_driver, vector_store_collection, embedding_driver):
        """Test basic vector CRUD, various call patterns."""
        vector_store_collection.delete_many({})

        vec1 = embedding_driver.embed_string("0.012")
        id1 = vector_store_driver.upsert_vector(vec1, vector_id="v1")

        vec2 = embedding_driver.embed_string("0.024")
        id2 = vector_store_driver.upsert_vector(vec2, vector_id="v2", namespace="ns")

        vec3 = embedding_driver.embed_string("0.036")
        id3 = vector_store_driver.upsert_vector(vec3)

        vec4 = embedding_driver.embed_string("0.048")
        id4 = vector_store_driver.upsert_vector(vec4, vector_id="v4", meta={"i": 4}, namespace="ns")

        assert id1 == "v1"
        assert id2 == "v2"
        assert isinstance(id3, str)
        assert id4 == "v4"

        # retrieve by id
        e1 = vector_store_driver.load_entry(id1)
        e1_n = vector_store_driver.load_entry(id1, namespace="false_ns")
        e2 = vector_store_driver.load_entry(id2, namespace="ns")
        e3 = vector_store_driver.load_entry(id3)
        e4 = vector_store_driver.load_entry(id4)
        assert e1 == BaseVectorStoreDriver.Entry(
            id=id1,
            vector=vec1,
        )
        assert e1_n is None
        assert e2 == BaseVectorStoreDriver.Entry(
            id=id2,
            vector=vec2,
            namespace="ns",
        )
        assert e3 == BaseVectorStoreDriver.Entry(
            id=id3,
            vector=vec3,
        )
        assert e4 == BaseVectorStoreDriver.Entry(
            id=id4,
            vector=vec4,
            meta={"i": 4},
            namespace="ns",
        )

        # retrieve multiple entries
        es_ns = vector_store_driver.load_entries(namespace="ns")
        es_all = vector_store_driver.load_entries()
        assert len(es_ns) == 2
        assert any(e == e2 for e in es_ns)
        assert any(e == e4 for e in es_ns)
        assert len(es_all) == 4
        assert any(e == e1 for e in es_all)
        assert any(e == e2 for e in es_all)
        assert any(e == e3 for e in es_all)
        assert any(e == e4 for e in es_all)

        # delete and recheck
        vector_store_driver.delete_vector("fake_id")
        vector_store_driver.delete_vector(id4)
        es_ns_postdel = vector_store_driver.load_entries(namespace="ns")
        assert len(es_ns_postdel) == 1
        assert es_ns_postdel[0] == e2

        # queries
        query_2 = vector_store_driver.query("0.060", count=2, include_vectors=True)
        query_all = vector_store_driver.query("0.060", include_vectors=True)
        query_2_novectors = vector_store_driver.query("0.060", count=2)
        query_all_ns = vector_store_driver.query("0.060", include_vectors=True, namespace="ns")
        #
        d_query_2 = [self._descore_entry(ent) for ent in query_2]
        assert d_query_2 == [e3, e2]

        d_query_all = [self._descore_entry(ent) for ent in query_all]
        assert d_query_all == [e3, e2, e1]
        d_query_2_novectors = [self._descore_entry(ent) for ent in query_2_novectors]
        assert d_query_2_novectors == [
            BaseVectorStoreDriver.Entry(
                id=id3,
            ),
            BaseVectorStoreDriver.Entry(
                id=id2,
                namespace="ns",
            ),
        ]
        d_query_all_ns = [self._descore_entry(ent) for ent in query_all_ns]
        assert d_query_all_ns == [e2]

    def _descore_entry(self, entry: BaseVectorStoreDriver.Entry) -> BaseVectorStoreDriver.Entry:
        return BaseVectorStoreDriver.Entry.from_dict({k: v for k, v in entry.__dict__.items() if k != "score"})
