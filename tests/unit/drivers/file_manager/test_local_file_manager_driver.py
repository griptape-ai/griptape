import os
import tempfile
from pathlib import Path

import pytest

from griptape.artifacts import InfoArtifact, ListArtifact, TextArtifact
from griptape.drivers import LocalFileManagerDriver
from griptape.loaders.text_loader import TextLoader


class TestLocalFileManagerDriver:
    @pytest.fixture()
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            def write_file(path: str, content: bytes) -> None:
                full_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                Path(full_path).write_bytes(content)

            def mkdir(path: str) -> None:
                full_path = os.path.join(temp_dir, path)
                os.makedirs(full_path, exist_ok=True)

            def copy_test_resources(resource_path: str) -> None:
                file_dir = os.path.dirname(__file__)
                full_path = os.path.join(file_dir, "../../../resources", resource_path)
                full_path = os.path.normpath(full_path)
                content = Path(full_path).read_bytes()
                dest_path = os.path.join(temp_dir, "resources", resource_path)
                write_file(dest_path, content)

            # Add some files
            write_file("foo.txt", b"foo")
            write_file("foo/bar.txt", b"bar")
            write_file("foo/bar/baz.txt", b"baz")
            copy_test_resources("bitcoin.pdf")
            copy_test_resources("small.png")
            copy_test_resources("test.txt")

            # Add some empty directories
            mkdir("foo-empty")
            mkdir("foo/bar-empty")
            mkdir("foo/bar/baz-empty")

            yield temp_dir

    @pytest.fixture()
    def driver(self, temp_dir):
        return LocalFileManagerDriver(workdir=temp_dir)

    def test_validate_workdir(self):
        with pytest.raises(ValueError):
            LocalFileManagerDriver(workdir="foo")

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # Valid non-empty directories (without trailing slash)
            ("/", "", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/", "foo", ["bar", "bar.txt", "bar-empty"]),
            ("/", "foo/bar", ["baz.txt", "baz-empty"]),
            ("/", "resources", ["bitcoin.pdf", "small.png", "test.txt"]),
            ("/foo", "", ["bar", "bar.txt", "bar-empty"]),
            ("/foo", "bar", ["baz.txt", "baz-empty"]),
            ("/foo/bar", "", ["baz.txt", "baz-empty"]),
            ("/resources", "", ["bitcoin.pdf", "small.png", "test.txt"]),
            # Valid non-empty directories (with trailing slash)
            ("/", "/", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/", "foo/", ["bar", "bar.txt", "bar-empty"]),
            ("/", "foo/bar/", ["baz.txt", "baz-empty"]),
            ("/foo", "/", ["bar", "bar.txt", "bar-empty"]),
            ("/foo", "bar/", ["baz.txt", "baz-empty"]),
            ("/foo/bar", "/", ["baz.txt", "baz-empty"]),
            # relative paths
            ("/", ".", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/", "foo/..", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/", "bar/..", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/", "foo/.", ["bar", "bar.txt", "bar-empty"]),
            ("/", "foo/bar/.", ["baz.txt", "baz-empty"]),
            ("/./..", ".", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/./..", "foo/..", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/./..", "bar/..", ["foo", "foo.txt", "foo-empty", "resources"]),
            ("/./..", "foo/.", ["bar", "bar.txt", "bar-empty"]),
            ("/./..", "foo/bar/.", ["baz.txt", "baz-empty"]),
            # Empty folders (without trailing slash)
            ("/", "foo-empty", []),
            ("/", "foo/bar-empty", []),
            ("/", "foo/bar/baz-empty", []),
            # Empty folders (with trailing slash)
            ("/", "foo-empty/", []),
            ("/", "foo/bar-empty/", []),
            ("/", "foo/bar/baz-empty/", []),
        ],
    )
    def test_list_files(self, workdir, path, expected, temp_dir, driver):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        driver.workdir = self._to_driver_workdir(temp_dir, workdir)

        artifact = driver.list_files(path)

        assert isinstance(artifact, TextArtifact)
        assert set(filter(None, artifact.value.split("\n"))) == set(expected)

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # non-existent paths
            ("/", "bar", FileNotFoundError),
            ("/", "bar/", FileNotFoundError),
            ("/", "bitcoin.pdf", FileNotFoundError),
            # # paths to files (not directories)
            ("/", "foo.txt", NotADirectoryError),
            ("/", "/foo.txt", NotADirectoryError),
            ("/resources", "bitcoin.pdf", NotADirectoryError),
            ("/resources", "/bitcoin.pdf", NotADirectoryError),
        ],
    )
    def test_list_files_failure(self, workdir, path, expected, temp_dir, driver):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        driver.workdir = self._to_driver_workdir(temp_dir, workdir)

        with pytest.raises(expected):
            driver.list_files(path)

    def test_load_file(self, driver: LocalFileManagerDriver):
        artifact = driver.load_file("resources/bitcoin.pdf")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 4

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # # non-existent files or directories
            ("/", "bitcoin.pdf", FileNotFoundError),
            ("/resources", "foo.txt", FileNotFoundError),
            ("/", "bar/", IsADirectoryError),
            # existing files with trailing slash
            ("/", "resources/bitcoin.pdf/", IsADirectoryError),
            ("/resources", "bitcoin.pdf/", IsADirectoryError),
            # directories -- not files
            ("/", "", IsADirectoryError),
            ("/", "/", IsADirectoryError),
            ("/", "resources", IsADirectoryError),
            ("/", "resources/", IsADirectoryError),
            ("/resources", "", IsADirectoryError),
            ("/resources", "/", IsADirectoryError),
        ],
    )
    def test_load_file_failure(self, workdir, path, expected, temp_dir, driver):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        driver.workdir = self._to_driver_workdir(temp_dir, workdir)

        with pytest.raises(expected):
            driver.load_file(path)

    def test_load_file_with_encoding(self, driver: LocalFileManagerDriver):
        artifact = driver.load_file("resources/test.txt")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)

    def test_load_file_with_encoding_failure(self, driver):
        driver = LocalFileManagerDriver(
            default_loader=TextLoader(encoding="utf-8"),
            loaders={},
            workdir=os.path.normpath(os.path.abspath(os.path.dirname(__file__) + "../../../../")),
        )

        with pytest.raises(UnicodeDecodeError):
            driver.load_file("resources/bitcoin.pdf")

    @pytest.mark.parametrize(
        ("workdir", "path", "content"),
        [
            # non-existent files
            ("/", "resources/foo.txt", "one"),
            ("/resources", "foo.txt", "two"),
            # existing files
            ("/", "foo.txt", "three"),
            ("/resources", "test.txt", "four"),
            ("/", "resources/test.txt", "five"),
            # binary content
            ("/", "bone.fooz", b"bone"),
        ],
    )
    def test_save_file(self, workdir, path, content, temp_dir, driver):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        driver.workdir = self._to_driver_workdir(temp_dir, workdir)

        result = driver.save_file(path, content)

        assert isinstance(result, InfoArtifact)
        assert result.value == "Successfully saved file"
        content_bytes = content if isinstance(content, str) else content.decode()
        assert Path(driver.workdir, path).read_text() == content_bytes

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # non-existent directories
            ("/", "bar/", IsADirectoryError),
            ("/", "/bar/", IsADirectoryError),
            # existing directories
            ("/", "", IsADirectoryError),
            ("/", "/", IsADirectoryError),
            ("/", "resources", IsADirectoryError),
            ("/", "resources/", IsADirectoryError),
            ("/resources", "", IsADirectoryError),
            ("/resources", "/", IsADirectoryError),
            # existing files with trailing slash
            ("/", "resources/bitcoin.pdf/", IsADirectoryError),
            ("/resources", "bitcoin.pdf/", IsADirectoryError),
        ],
    )
    def test_save_file_failure(self, workdir, path, expected, temp_dir, driver):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        driver.workdir = self._to_driver_workdir(temp_dir, workdir)

        with pytest.raises(expected):
            driver.save_file(path, "foobar")

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

    def _to_driver_workdir(self, temp_dir, workdir):
        # Treat the workdir as an absolute path, but modify it to be relative to the temp_dir.
        root_relative_parts = Path(os.path.abspath(workdir)).parts[1:]
        return os.path.join(temp_dir, Path(*root_relative_parts))
