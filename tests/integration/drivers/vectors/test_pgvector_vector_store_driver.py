import uuid
import pytest
from griptape.drivers import PgVectorVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestPgVectorVectorStoreDriver:
    vec1 = [0.1, 0.2, 0.3]
    vec2 = [0.4, 0.5, 0.6]

    @pytest.fixture
    def embedding_driver(self):
        return MockEmbeddingDriver()

    @pytest.fixture
    def vector_store_driver(self, embedding_driver):
        driver = PgVectorVectorStoreDriver(
            connection_string="postgresql://postgres:postgres@localhost:5432/postgres",
            embedding_driver=embedding_driver,
        )

        driver.install_postgres_extensions()
        driver.create_schema()

        return driver

    def test_can_insert_vector(self, vector_store_driver):
        result = vector_store_driver.upsert_vector(self.vec1)

        assert result is not None

    def test_can_insert_vector_with_id(self, vector_store_driver):
        vector_id = str(uuid.uuid4())

        result = vector_store_driver.upsert_vector(self.vec1, vector_id=vector_id)

        assert result == vector_id

    def test_can_update_vector_by_id(self, vector_store_driver):
        vector_id = str(uuid.uuid4())

        result = vector_store_driver.upsert_vector(self.vec1, vector_id=vector_id)
        assert result == vector_id

        result = vector_store_driver.upsert_vector(self.vec2, vector_id=vector_id)
        assert result == vector_id

        result = vector_store_driver.load_entry(vector_id)
        assert result.vector == pytest.approx(self.vec2)

    def test_can_load_entry_by_id(self, vector_store_driver):
        result = vector_store_driver.upsert_vector(self.vec1)
        assert result is not None

        result = vector_store_driver.load_entry(result)
        assert result.vector == pytest.approx(self.vec1)

    def test_can_insert_and_load_entry_with_namespace(self, vector_store_driver):
        namespace = str(uuid.uuid4())

        result = vector_store_driver.upsert_vector(self.vec1, namespace=namespace)
        assert result is not None

        result = vector_store_driver.load_entry(result, namespace=namespace)
        assert result.vector == pytest.approx(self.vec1)

    def test_can_load_entries(self, vector_store_driver):
        """
        Depending on when this test is executed relative to the others,
        we don't know exactly how many vectors will be returned. We can
        ensure that at least two exist and confirm that those are found.
        """
        vec1_id = vector_store_driver.upsert_vector(self.vec1)
        vec2_id = vector_store_driver.upsert_vector(self.vec2)

        results = vector_store_driver.load_entries()

        assert len(results) >= 2
        assert vec1_id in [result.id for result in results]
        assert vec2_id in [result.id for result in results]

        vectors_by_id = {result.id: result.vector for result in results}
        assert vectors_by_id[vec1_id] == pytest.approx(self.vec1)
        assert vectors_by_id[vec2_id] == pytest.approx(self.vec2)

    def test_can_load_by_namespace(self, vector_store_driver):
        namespace = str(uuid.uuid4())

        vec1_id = vector_store_driver.upsert_vector(self.vec1, namespace=namespace)
        vec2_id = vector_store_driver.upsert_vector(self.vec2, namespace=namespace)

        results = vector_store_driver.load_entries(namespace=namespace)

        assert len(results) == 2
        assert vec1_id in [result.id for result in results]
        assert vec2_id in [result.id for result in results]

        vectors_by_id = {result.id: result.vector for result in results}
        assert vectors_by_id[vec1_id] == pytest.approx(self.vec1)
        assert vectors_by_id[vec2_id] == pytest.approx(self.vec2)

    def test_can_query(self, vector_store_driver):
        value = "my string here"
        namespace = str(uuid.uuid4())
        embedding = vector_store_driver.embedding_driver.embed_string(value)

        vector_store_driver.upsert_vector(embedding, namespace=namespace)
        results = vector_store_driver.query(value, namespace=namespace)

        assert len(results) == 1

    def test_can_query_by_cosine_distance(self, vector_store_driver):
        value = "my string here"
        namespace = str(uuid.uuid4())
        embedding = vector_store_driver.embedding_driver.embed_string(value)

        vector_store_driver.upsert_vector(embedding, namespace=namespace)
        results = vector_store_driver.query(value, namespace=namespace, distance_metric="cosine_distance")

        assert len(results) == 1

    def test_can_query_by_l2_distance(self, vector_store_driver):
        value = "my string here"
        namespace = str(uuid.uuid4())
        embedding = vector_store_driver.embedding_driver.embed_string(value)

        vector_store_driver.upsert_vector(embedding, namespace=namespace)
        results = vector_store_driver.query(value, namespace=namespace, distance_metric="l2_distance")

        assert len(results) == 1

    def test_can_query_by_inner_product(self, vector_store_driver):
        value = "my string here"
        namespace = str(uuid.uuid4())
        embedding = vector_store_driver.embedding_driver.embed_string(value)

        vector_store_driver.upsert_vector(embedding, namespace=namespace)
        results = vector_store_driver.query(value, namespace=namespace, distance_metric="inner_product")

        assert len(results) == 1

    def test_query_returns_vectors_when_requested(self, vector_store_driver):
        value = "my string here"
        namespace = str(uuid.uuid4())
        embedding = vector_store_driver.embedding_driver.embed_string(value)

        vector_store_driver.upsert_vector(embedding, namespace=namespace)
        results = vector_store_driver.query(value, namespace=namespace, include_vectors=True)

        assert len(results) == 1
        assert results[0].vector == pytest.approx(embedding)
