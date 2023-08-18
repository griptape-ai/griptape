import os.path
import tempfile
from griptape.artifacts import BlobArtifact, TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.tools import FileManager


class TestFileManager:
    def test_load_files_from_disk(self):
        result = FileManager(
            input_memory=[TextToolMemory()],
            dir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["resources/bitcoin.pdf"]}})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], BlobArtifact)

    def test_save_file_to_disk(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver())))
            artifact = TextArtifact("foobar")
            path = os.path.join(temp_dir, "foobar.txt")

            memory.query_engine.vector_store_driver.upsert_text_artifact(artifact, namespace="foobar")

            result = FileManager(
                input_memory=[memory]
            ).save_file_to_disk({"values": {"path": path, "memory_id": memory.id, "artifact_namespace": "foobar"}})

            assert result.value == "saved successfully"
