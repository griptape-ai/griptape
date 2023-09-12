import os.path
import tempfile
from pathlib import Path
from griptape.artifacts import BlobArtifact, TextArtifact, ListArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import ToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from griptape.tools import FileManager


class TestFileManager:
    def test_load_files_from_disk(self):
        result = FileManager(
            input_memory=[ToolMemory()],
            dir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], BlobArtifact)

    def test_save_memory_artifacts_to_disk_for_one_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = ToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver())))
            artifact = TextArtifact("foobar")

            memory.query_engine.vector_store_driver.upsert_text_artifact(artifact, namespace="foobar")

            result = FileManager(
                dir=temp_dir,
                input_memory=[memory]
            ).save_memory_artifacts_to_disk(
                {
                    "values":
                        {
                            "dir_name": "test",
                            "file_name": "foobar.txt",
                            "memory_name": memory.name,
                            "artifact_namespace": "foobar"
                        }
                }
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

    def test_save_memory_artifacts_to_disk_for_multiple_artifacts(self):
        file_name = "foobar.txt"

        with tempfile.TemporaryDirectory() as temp_dir:
            memory = ToolMemory(
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
                dir=temp_dir,
                input_memory=[memory]
            ).save_memory_artifacts_to_disk(
                {
                    "values":
                        {
                            "dir_name": "test",
                            "file_name": file_name,
                            "memory_name": memory.name,
                            "artifact_namespace": "foobar"
                        }
                }
            )

            assert Path(os.path.join(temp_dir, "test", f"{artifacts[0].name}-{file_name}")).read_text() == "foobar"
            assert Path(os.path.join(temp_dir, "test", f"{artifacts[1].name}-{file_name}")).read_text() == "baz"
            assert result.value == "saved successfully"

    def test_save_content_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(
                dir=temp_dir
            ).save_content_to_file(
                {
                    "values":
                        {
                            "path": os.path.join("test", "foobar.txt"),
                            "content": "foobar"
                        }
                }
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"
