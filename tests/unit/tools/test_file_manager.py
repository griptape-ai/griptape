import os
import os.path
import tempfile
from pathlib import Path

import pytest

from griptape.artifacts import CsvRowArtifact, ListArtifact, TextArtifact
from griptape.drivers.file_manager.local_file_manager_driver import LocalFileManagerDriver
from griptape.loaders.text_loader import TextLoader
from griptape.tools import FileManagerTool
from tests.utils import defaults


class TestFileManager:
    @pytest.fixture()
    def file_manager(self):
        return FileManagerTool(
            input_memory=[defaults.text_task_memory("Memory1")],
            file_manager_driver=LocalFileManagerDriver(workdir=os.path.abspath(os.path.dirname(__file__))),
        )

    @pytest.fixture()
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_list_files_from_disk(self, file_manager):
        result = file_manager.list_files_from_disk({"values": {"path": "../../resources"}})

        assert isinstance(result, TextArtifact)
        assert "bitcoin.pdf" in result.value
        assert "small.png" in result.value

    def test_load_files_from_disk(self, file_manager):
        result = file_manager.load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 4

    def test_load_files_from_disk_with_encoding(self, file_manager):
        result = file_manager.load_files_from_disk({"values": {"paths": ["../../resources/test.txt"]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)

    def test_load_files_from_disk_with_encoding_failure(self):
        file_manager = FileManagerTool(
            file_manager_driver=LocalFileManagerDriver(
                default_loader=TextLoader(encoding="utf-8"),
                loaders={},
                workdir=os.path.abspath(os.path.dirname(__file__)),
            )
        )

        with pytest.raises(UnicodeDecodeError):
            file_manager.load_files_from_disk({"values": {"paths": ["../../resources/bitcoin.pdf"]}})

    def test_save_memory_artifacts_to_disk_for_one_artifact(self, temp_dir):
        memory = defaults.text_task_memory("Memory1")
        artifact = TextArtifact("foobar")

        memory.store_artifact("foobar", artifact)

        file_manager = FileManagerTool(
            input_memory=[memory], file_manager_driver=LocalFileManagerDriver(workdir=temp_dir)
        )
        result = file_manager.save_memory_artifacts_to_disk(
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
        assert result.value == "Successfully saved memory artifacts to disk"

    def test_save_memory_artifacts_to_disk_for_multiple_artifacts(self, temp_dir):
        file_name = "foobar.txt"
        memory = defaults.text_task_memory("Memory1")
        artifacts = [TextArtifact("foobar"), TextArtifact("baz")]

        for a in artifacts:
            memory.store_artifact("foobar", a)

        file_manager = FileManagerTool(
            input_memory=[memory], file_manager_driver=LocalFileManagerDriver(workdir=temp_dir)
        )
        result = file_manager.save_memory_artifacts_to_disk(
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
        assert result.value == "Successfully saved memory artifacts to disk"

    def test_save_memory_artifacts_to_disk_for_non_string_artifact(self, temp_dir):
        memory = defaults.text_task_memory("Memory1")
        artifact = CsvRowArtifact({"foo": "bar"})

        memory.store_artifact("foobar", artifact)

        file_manager = FileManagerTool(
            input_memory=[memory], file_manager_driver=LocalFileManagerDriver(workdir=temp_dir)
        )
        result = file_manager.save_memory_artifacts_to_disk(
            {
                "values": {
                    "dir_name": "test",
                    "file_name": "foobar.txt",
                    "memory_name": memory.name,
                    "artifact_namespace": "foobar",
                }
            }
        )

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foo\nbar"
        assert result.value == "Successfully saved memory artifacts to disk"

    def test_save_content_to_file(self, temp_dir):
        file_manager = FileManagerTool(file_manager_driver=LocalFileManagerDriver(workdir=temp_dir))
        result = file_manager.save_content_to_file(
            {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
        )

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

    def test_save_content_to_file_with_encoding(self, temp_dir):
        file_manager = FileManagerTool(
            file_manager_driver=LocalFileManagerDriver(default_loader=TextLoader(encoding="utf-8"), workdir=temp_dir)
        )
        result = file_manager.save_content_to_file(
            {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
        )

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

    def test_save_and_load_content_to_file_with_encoding(self, temp_dir):
        file_manager = FileManagerTool(
            file_manager_driver=LocalFileManagerDriver(loaders={"txt": TextLoader(encoding="ascii")}, workdir=temp_dir)
        )
        result = file_manager.save_content_to_file(
            {"values": {"path": os.path.join("test", "foobar.txt"), "content": "foobar"}}
        )

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

        file_manager = FileManagerTool(
            file_manager_driver=LocalFileManagerDriver(
                default_loader=TextLoader(encoding="ascii"), loaders={}, workdir=temp_dir
            )
        )
        result = file_manager.load_files_from_disk({"values": {"paths": [os.path.join("test", "foobar.txt")]}})

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)
