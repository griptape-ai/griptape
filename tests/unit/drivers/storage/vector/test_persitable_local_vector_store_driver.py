import tempfile

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import PersistableLocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class Tests:
    def t_persistable_vector_store(self,suffix : str):
        with tempfile.NamedTemporaryFile() as f:
            file_name = f.name+f".{suffix}"
            vector_store = PersistableLocalVectorStoreDriver(
                file_path=file_name, embedding_driver=MockEmbeddingDriver()
            )
            artifact = TextArtifact(value="Long live the queen!")
            vector_store.upsert_text_artifact(artifact)
            vector_store.store(
                overwrite=True
            )  # need to overwrite since tempfile created the file
            old_vector_store_entries = vector_store.entries
            del vector_store
            new_vector_store = PersistableLocalVectorStoreDriver.from_saved(
                file_path=file_name
            )
            _, value = old_vector_store_entries.popitem()
            _, new_value = new_vector_store.entries.popitem()
            assert value == new_value

    def test_save_load_json(self):
        self.t_persistable_vector_store("json")

    def test_save_load_zip(self):
        self.t_persistable_vector_store("json")
    def test_suffix_raises(self):
        with pytest.raises(ValueError) as e_info:
            with tempfile.NamedTemporaryFile() as f:
                vector_store = PersistableLocalVectorStoreDriver(
                    file_path=f.name, embedding_driver=MockEmbeddingDriver()
                )
            assert str(e_info.value) == "file must either be a json or a zip"
