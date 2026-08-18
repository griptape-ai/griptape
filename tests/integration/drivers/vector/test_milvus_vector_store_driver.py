import uuid

import pytest

from griptape.drivers.vector.milvus import MilvusVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

pymilvus = pytest.importorskip("pymilvus")


class TestMilvusVectorStoreDriver:
    @pytest.fixture()
    def embedding_driver(self):
        def mock_output(value):
            text = value.to_text() if hasattr(value, "to_text") else str(value)

            if "beta" in text.lower():
                return [0.0, 1.0]
            return [1.0, 0.0]

        return MockEmbeddingDriver(mock_output=mock_output)

    @pytest.fixture()
    def vector_store_driver(self, tmp_path, embedding_driver):
        return MilvusVectorStoreDriver(
            uri=str(tmp_path / "milvus.db"),
            collection_name=f"griptape_milvus_test_{uuid.uuid4().hex}",
            embedding_driver=embedding_driver,
            vector_dim=2,
        )

    def test_can_insert_update_load_and_delete_vector(self, vector_store_driver):
        vector_id = "alpha"

        result = vector_store_driver.upsert_vector(
            [1.0, 0.0],
            vector_id=vector_id,
            namespace="docs",
            meta={"source": "guide", "rank": 1},
        )
        assert result == vector_id

        entry = vector_store_driver.load_entry(vector_id, namespace="docs")
        assert entry is not None
        assert entry.vector == pytest.approx([1.0, 0.0])
        assert entry.namespace == "docs"
        assert entry.meta == {"source": "guide", "rank": 1}

        vector_store_driver.upsert_vector(
            [0.0, 1.0],
            vector_id=vector_id,
            namespace="docs",
            meta={"source": "guide", "rank": 2},
        )
        entry = vector_store_driver.load_entry(vector_id, namespace="docs")
        assert entry is not None
        assert entry.vector == pytest.approx([0.0, 1.0])
        assert entry.meta == {"source": "guide", "rank": 2}

        vector_store_driver.delete_vector(vector_id)

        assert vector_store_driver.load_entry(vector_id, namespace="docs") is None

    def test_can_load_entries_by_namespace(self, vector_store_driver):
        docs_id = vector_store_driver.upsert_vector([1.0, 0.0], namespace="docs")
        notes_id = vector_store_driver.upsert_vector([0.0, 1.0], namespace="notes")

        entries = vector_store_driver.load_entries(namespace="docs")

        assert [entry.id for entry in entries] == [docs_id]
        assert notes_id not in [entry.id for entry in entries]

    def test_can_query_with_namespace_and_filter(self, vector_store_driver):
        vector_store_driver.upsert_vector(
            [1.0, 0.0],
            vector_id="alpha",
            namespace="docs",
            meta={"source": "guide", "rank": 1},
        )
        vector_store_driver.upsert_vector(
            [0.0, 1.0],
            vector_id="beta",
            namespace="docs",
            meta={"source": "reference", "rank": 2},
        )
        vector_store_driver.upsert_vector(
            [1.0, 0.0],
            vector_id="gamma",
            namespace="notes",
            meta={"source": "guide", "rank": 1},
        )

        results = vector_store_driver.query_vector(
            [1.0, 0.0],
            namespace="docs",
            include_vectors=True,
            filter={"source": "guide", "rank": [1, 3]},
        )

        assert len(results) == 1
        assert results[0].id == "alpha"
        assert results[0].vector == pytest.approx([1.0, 0.0])
        assert results[0].score == pytest.approx(1.0)
        assert results[0].meta == {"source": "guide", "rank": 1}
        assert results[0].namespace == "docs"

    def test_can_query_text(self, vector_store_driver):
        vector_id = vector_store_driver.upsert("alpha document", namespace="docs", meta={"source": "guide"})

        results = vector_store_driver.query("alpha", namespace="docs")

        assert len(results) == 1
        assert results[0].id == vector_id
        assert results[0].to_artifact().value == "alpha document"

    def test_rejects_vector_dimension_mismatch(self, vector_store_driver):
        vector_store_driver.upsert_vector([1.0, 0.0])

        with pytest.raises(ValueError, match="vector dimension"):
            vector_store_driver.upsert_vector([1.0, 0.0, 0.0])
