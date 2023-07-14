import tempfile

from griptape.artifacts import TextArtifact
from griptape.drivers import PersistableLocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class Tests:
    def test_persistable_vector_store(self):
        with tempfile.NamedTemporaryFile() as f:
            vector_store = PersistableLocalVectorStoreDriver(
                file_path=f.name, embedding_driver=MockEmbeddingDriver()
            )
            artifact = TextArtifact(value="Long live the queen!")
            vector_store.upsert_text_artifact(artifact)
            vector_store.store(
                overwrite=True
            )  # need to overwrite since tempfile created the file
            old_vector_store_entries = vector_store.entries
            del vector_store
            new_vector_store = PersistableLocalVectorStoreDriver().from_saved(
                file_path=f.name
            )
            k, v = old_vector_store_entries.popitem()
            kn, vn = new_vector_store.entries.popitem()
            assert v == vn
