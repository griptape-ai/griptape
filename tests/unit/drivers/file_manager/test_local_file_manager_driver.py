import os
from pathlib import Path
import tempfile
import pytest
from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.drivers import LocalFileManagerDriver
from griptape.loaders.text_loader import TextLoader


class TestLocalFileManagerDriver:
    @pytest.fixture
    def driver(self):
        tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        return LocalFileManagerDriver(workdir=tests_dir)

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_validate_workdir(self):
        with pytest.raises(ValueError):
            LocalFileManagerDriver(workdir="foo")

    def test_list_files(self, driver: LocalFileManagerDriver):
        artifact = driver.list_files("resources")

        assert isinstance(artifact, TextArtifact)
        assert "bitcoin.pdf" in artifact.value
        assert "small.png" in artifact.value

    def test_load_file(self, driver: LocalFileManagerDriver):
        artifact = driver.load_file("resources/bitcoin.pdf")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 4

    def test_load_file_with_encoding(self, driver: LocalFileManagerDriver):
        artifact = driver.load_file("resources/test.txt")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)

    def test_load_file_with_encoding_failure(self):
        driver = LocalFileManagerDriver(
            default_loader=TextLoader(encoding="utf-8"), loaders={}, workdir=os.path.abspath(os.path.dirname(__file__))
        )

        artifact = driver.load_file("resources/bitcoin.pdf")

        assert isinstance(artifact, ErrorArtifact)

    def test_save_file(self, temp_dir):
        driver = LocalFileManagerDriver(workdir=temp_dir)
        result = driver.save_file(os.path.join("test", "foobar.txt"), "foobar")

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

    def test_save_file_with_encoding(self, temp_dir):
        driver = LocalFileManagerDriver(default_loader=TextLoader(encoding="utf-8"), loaders={}, workdir=temp_dir)
        result = driver.save_file(os.path.join("test", "foobar.txt"), "foobar")

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

    def test_save_and_load_file_with_encoding(self, temp_dir):
        driver = LocalFileManagerDriver(loaders={"txt": TextLoader(encoding="ascii")}, workdir=temp_dir)
        result = driver.save_file(os.path.join("test", "foobar.txt"), "foobar")

        assert Path(os.path.join(temp_dir, "test", "foobar.txt")).read_text() == "foobar"
        assert result.value == "Successfully saved file"

        driver = LocalFileManagerDriver(default_loader=TextLoader(encoding="ascii"), loaders={}, workdir=temp_dir)
        result = driver.load_file(os.path.join("test", "foobar.txt"))

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)

    def test_chrdir_getcwd(self, temp_dir):
        os.chdir(temp_dir)
        file_manager_1 = LocalFileManagerDriver()
        assert file_manager_1.workdir.endswith(temp_dir)
        os.chdir("/tmp")
        file_manager_2 = LocalFileManagerDriver()
        assert file_manager_2.workdir.endswith("/tmp")
