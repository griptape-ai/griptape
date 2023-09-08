import os.path
import tempfile
from griptape.artifacts import BlobArtifact, TextArtifact, ListArtifact
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

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], BlobArtifact)

    def test_save_file_to_disk_from_memory(self):
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
            ).save_file_to_disk(
                {
                    "values":
                        {
                            "path": path,
                            "data": {
                                "memory_name": memory.name,
                                "artifact_namespace": "foobar"
                            }
                        }
                }
            )

            assert result.value == "saved successfully"

    def test_save_file_to_disk_from_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "foobar.txt")

            result = FileManager(
            ).save_file_to_disk(
                {
                    "values":
                        {
                            "path": path,
                            "data": {
                                "content": "foobar"
                            }
                        }
                }
            )

            assert result.value == "saved successfully"
