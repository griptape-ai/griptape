import os.path
import tempfile
from pathlib import Path
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

    def test_save_memory_artifacts_to_disk_for_one_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver())))
            artifact = TextArtifact("foobar")

            memory.query_engine.vector_store_driver.upsert_text_artifact(artifact, namespace="foobar")

            result = FileManager(
                input_memory=[memory]
            ).save_memory_artifacts_to_disk(
                {
                    "values":
                        {
                            "path": temp_dir,
                            "filename": "foobar.txt",
                            "memory_name": memory.name,
                            "artifact_namespace": "foobar"
                        }
                }
            )

            assert Path(os.path.join(temp_dir, "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

    def test_save_memory_artifacts_to_disk_for_multiple_artifacts(self):
        filename = "foobar.txt"

        with tempfile.TemporaryDirectory() as temp_dir:
            memory = TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver())))
            artifacts = [
                TextArtifact("foobar"),
                TextArtifact("baz")
            ]

            for a in artifacts:
                memory.query_engine.vector_store_driver.upsert_text_artifact(a, namespace="foobar")

            result = FileManager(
                input_memory=[memory]
            ).save_memory_artifacts_to_disk(
                {
                    "values":
                        {
                            "path": temp_dir,
                            "filename": filename,
                            "memory_name": memory.name,
                            "artifact_namespace": "foobar"
                        }
                }
            )

            assert Path(os.path.join(temp_dir, f"{artifacts[0].name}-{filename}")).read_text() == "foobar"
            assert Path(os.path.join(temp_dir, f"{artifacts[1].name}-{filename}")).read_text() == "baz"
            assert result.value == "saved successfully"

    def test_save_content_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "foobar.txt")

            result = FileManager(
            ).save_content_to_file(
                {
                    "values":
                        {
                            "path": path,
                            "content": "foobar"
                        }
                }
            )

            assert result.value == "saved successfully"
