from __future__ import annotations

import json
import math
import os

import pytest
from attrs import define, field

from griptape.drivers import AstraDBVectorStoreDriver, BaseEmbeddingDriver, BaseVectorStoreDriver
from tests.mocks.mock_tokenizer import MockTokenizer

TEST_COLLECTION_NAME = "gt_int_test"


def astrapy_available() -> bool:
    try:
        return True
    except Exception:
        return False


def astra_db_available() -> bool:
    return all(
        [
            "ASTRA_DB_APPLICATION_TOKEN" in os.environ,
            "ASTRA_DB_API_ENDPOINT" in os.environ,
        ]
    )


def _descore_entry(entry: BaseVectorStoreDriver.Entry) -> BaseVectorStoreDriver.Entry:
    return BaseVectorStoreDriver.Entry.from_dict({k: v for k, v in entry.__dict__.items() if k != "score"})


@define
class ParserEmbeddingDriver(BaseEmbeddingDriver):
    model: str = field(default="foo", kw_only=True)
    dimensions: int = field(default=2, kw_only=True)
    max_attempts: int = field(default=1, kw_only=True)
    tokenizer: MockTokenizer = field(factory=lambda: MockTokenizer(model="foo bar"), kw_only=True)

    def try_embed_chunk(self, chunk: str) -> list[float]:
        vector2d: list[float]
        try:
            fraction = float(json.loads(chunk))
            angle = fraction * math.pi * 2
            vector2d = [math.cos(angle), math.sin(angle)]
        except Exception:
            vector2d = [0.0, 0.0]
        return (vector2d + [0] * (self.dimensions))[: self.dimensions]


@pytest.mark.skipif(not astrapy_available(), reason="Package astrapy not installed")
@pytest.mark.skipif(not astra_db_available(), reason="No connection info for Astra DB")
class TestAstraDBVectorStoreDriver:
    @pytest.fixture()
    def embedding_driver(self):
        return ParserEmbeddingDriver()

    @pytest.fixture()
    def vector_store_driver(self, embedding_driver):
        driver = AstraDBVectorStoreDriver(
            api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
            token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
            collection_name=TEST_COLLECTION_NAME,
            astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
            embedding_driver=embedding_driver,
        )
        return driver
        driver.collection.drop()

    @pytest.fixture()
    def vector_store_collection(self, vector_store_driver):
        """For testing purposes, access the bare AstraPy "Collection"."""
        return vector_store_driver.collection

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
        d_query_2 = [_descore_entry(ent) for ent in query_2]
        assert d_query_2 == [e3, e2]

        d_query_all = [_descore_entry(ent) for ent in query_all]
        assert d_query_all == [e3, e2, e1]
        d_query_2_novectors = [_descore_entry(ent) for ent in query_2_novectors]
        assert d_query_2_novectors == [
            BaseVectorStoreDriver.Entry(
                id=id3,
            ),
            BaseVectorStoreDriver.Entry(
                id=id2,
                namespace="ns",
            ),
        ]
        d_query_all_ns = [_descore_entry(ent) for ent in query_all_ns]
        assert d_query_all_ns == [e2]

    def test_explicit_dimension(self, vector_store_driver, embedding_driver):
        AstraDBVectorStoreDriver(
            api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
            token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
            collection_name=TEST_COLLECTION_NAME,
            astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
            dimension=2,
            embedding_driver=embedding_driver,
        )
        import astrapy

        with pytest.raises(astrapy.exceptions.DataAPIException):
            AstraDBVectorStoreDriver(
                api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
                token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
                collection_name=TEST_COLLECTION_NAME,
                astra_db_namespace=os.environ.get("ASTRA_DB_KEYSPACE"),
                dimension=123,
                embedding_driver=embedding_driver,
            )
