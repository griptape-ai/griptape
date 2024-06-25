import pytest
from griptape.drivers import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.drivers.vector.test_base_local_vector_store_driver import BaseLocalVectorStoreDriver


class TestInMemoryLocalVectorStoreDriver(BaseLocalVectorStoreDriver):
    @pytest.fixture
    def driver(self):
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())
