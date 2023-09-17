import os.path
import tempfile
from pathlib import Path
import pytest
from griptape.artifacts import ErrorArtifact
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine, PromptSummaryEngine
from griptape.memory.tool import TextToolMemory
from griptape.tools import FileManager
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestFileManager:
    def test_validate_workdir(self):
        with pytest.raises(ValueError):
            FileManager(workdir="foo")

    def test_load_files_from_disk(self):
        result = FileManager(
            input_memory=[
                TextToolMemory(
                    query_engine=VectorQueryEngine(
                        vector_store_driver=LocalVectorStoreDriver(
                            embedding_driver=MockEmbeddingDriver()
                        )
                    ),
                    summary_engine=PromptSummaryEngine()
                )
            ],
            workdir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        
    def test_load_files_from_disk_with_encoding(self):
        result = FileManager(
            load_file_encoding='utf-8',
            workdir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["../../resources/test.txt"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)

    def test_load_files_from_disk_with_encoding_failure(self):
        result = FileManager(
            load_file_encoding='utf-8',
            workdir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result.value[0], ErrorArtifact)

    def test_save_memory_artifacts_to_disk_for_one_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver()
                    )
                ),
                summary_engine=PromptSummaryEngine()
            )
            artifact = TextArtifact("foobar")

            memory.query_engine.vector_store_driver.upsert_text_artifact(artifact, namespace="foobar")

            result = FileManager(
                workdir=temp_dir,
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
            memory = TextToolMemory(
                query_engine=VectorQueryEngine(
                    vector_store_driver=LocalVectorStoreDriver(
                        embedding_driver=MockEmbeddingDriver()
                    )
                ),
                summary_engine=PromptSummaryEngine()
            )
            artifacts = [
                TextArtifact("foobar"),
                TextArtifact("baz")
            ]

            for a in artifacts:
                memory.query_engine.vector_store_driver.upsert_text_artifact(a, namespace="foobar")

            result = FileManager(
                workdir=temp_dir,
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
                workdir=temp_dir
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

    def test_save_content_to_file_with_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(
                workdir=temp_dir,
                save_file_encoding='utf-8'
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

    def test_save_and_load_content_to_file_with_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(
                workdir=temp_dir,
                save_file_encoding='ascii'
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

            result = FileManager(
                workdir=temp_dir,
                load_file_encoding='ascii'
            ).load_files_from_disk(
                {
                    "values":
                        {
                            "paths": [os.path.join("test", "foobar.txt")],
                        }
                }
            )

            assert isinstance(result, ListArtifact)
            assert len(result.value) == 1
            assert isinstance(result.value[0], TextArtifact)
