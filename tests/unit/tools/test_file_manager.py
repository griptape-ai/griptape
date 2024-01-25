import os.path
import os
import tempfile
from pathlib import Path
import pytest
from griptape.artifacts import ErrorArtifact
from griptape.artifacts import TextArtifact, ListArtifact
from griptape.loaders import FileLoader
from griptape.tools import FileManager
from tests.utils import defaults


class TestFileManager:
    def test_validate_workdir(self):
        with pytest.raises(ValueError):
            FileManager(workdir="foo")

    def test_load_files_from_disk(self):
        result = FileManager(
            input_memory=[defaults.text_task_memory("Memory1")], workdir=os.path.abspath(os.path.dirname(__file__))
        ).load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 4

    def test_load_files_from_disk_with_encoding(self):
        result = FileManager(workdir=os.path.abspath(os.path.dirname(__file__))).load_files_from_disk(
            {"values": {"paths": ["../../resources/test.txt"]}}
        )

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)

    def test_load_files_from_disk_with_encoding_failure(self):
        result = FileManager(
            workdir=os.path.abspath(os.path.dirname(__file__)), default_loader=FileLoader(encoding="utf-8"), loaders={}
        ).load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result.value[0], ErrorArtifact)

    def test_save_memory_artifacts_to_disk_for_one_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = defaults.text_task_memory("Memory1")
            artifact = TextArtifact("foobar")

            memory.store_artifact("foobar", artifact)

            result = FileManager(workdir=temp_dir, input_memory=[memory]).save_memory_artifacts_to_disk(
                {
                    "values": {
                        "dir_name": "test",
                        "file_name": "foobar.txt",
                        "memory_name": memory.name,
                        "artifact_namespace": "foobar",
                    }
                }
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

    def test_save_memory_artifacts_to_disk_for_multiple_artifacts(self):
        file_name = "foobar.txt"

        with tempfile.TemporaryDirectory() as temp_dir:
            memory = defaults.text_task_memory("Memory1")
            artifacts = [TextArtifact("foobar"), TextArtifact("baz")]

            for a in artifacts:
                memory.store_artifact("foobar", a)

            result = FileManager(workdir=temp_dir, input_memory=[memory]).save_memory_artifacts_to_disk(
                {
                    "values": {
                        "dir_name": "test",
                        "file_name": file_name,
                        "memory_name": memory.name,
                        "artifact_namespace": "foobar",
                    }
                }
            )

            assert Path(os.path.join(temp_dir, "test", f"{artifacts[0].name}-{file_name}")).read_text() == "foobar"
            assert Path(os.path.join(temp_dir, "test", f"{artifacts[1].name}-{file_name}")).read_text() == "baz"
            assert result.value == "saved successfully"

    def test_save_content_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(workdir=temp_dir).save_content_to_file(
                {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

    def test_save_content_to_file_with_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(workdir=temp_dir, save_file_encoding="utf-8").save_content_to_file(
                {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

    def test_save_and_load_content_to_file_with_encoding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = FileManager(workdir=temp_dir, save_file_encoding="ascii").save_content_to_file(
                {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
            )

            assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
            assert result.value == "saved successfully"

            result = FileManager(
                workdir=temp_dir, default_loader=FileLoader(encoding="ascii"), loaders={}
            ).load_files_from_disk({"values": {"paths": [os.path.join("test", "foobar.txt")]}})

            assert isinstance(result, ListArtifact)
            assert len(result.value) == 1
            assert isinstance(result.value[0], TextArtifact)

    def test_chrdir_getcwd(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            file_manager_1 = FileManager()
            assert file_manager_1.workdir.endswith(temp_dir)
            os.chdir("/tmp")
            file_manager_2 = FileManager()
            assert file_manager_2.workdir.endswith("/tmp")
