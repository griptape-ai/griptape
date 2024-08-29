import os
import tempfile

import boto3
import pytest
from moto import mock_s3

from griptape.artifacts import InfoArtifact, ListArtifact, TextArtifact
from griptape.drivers import AmazonS3FileManagerDriver
from griptape.loaders import TextLoader
from tests.utils.aws import mock_aws_credentials


class TestAmazonS3FileManagerDriver:
    @pytest.fixture(autouse=True)
    def _set_aws_credentials(self):
        mock_aws_credentials()

    @pytest.fixture()
    def session(self):
        mock = mock_s3()
        mock.start()
        yield boto3.Session(region_name="us-east-1")
        mock.stop()

    @pytest.fixture()
    def s3_client(self, session):
        return session.client("s3")

    @pytest.fixture(autouse=True)
    def bucket(self, s3_client):
        bucket = "test-bucket"
        s3_client.create_bucket(Bucket=bucket)

        def write_file(path: str, content: bytes) -> None:
            s3_client.put_object(Bucket=bucket, Key=path, Body=content)

        def mkdir(path: str) -> None:
            # S3-style empty directories, such as is created via the `Create Folder` button
            # in the AWS S3 console (essentially, an empty file with a trailing slash).
            s3_dir_key = path.rstrip("/") + "/"
            s3_client.put_object(Bucket=bucket, Key=s3_dir_key)

        def copy_test_resource(resource_path: str) -> None:
            file_dir = os.path.dirname(__file__)
            full_path = os.path.join(file_dir, "../../../resources", resource_path)
            full_path = os.path.normpath(full_path)
            s3_client.upload_file(Bucket=bucket, Key=f"resources/{resource_path}", Filename=full_path)

        # Add some files
        write_file("foo.txt", b"foo")
        write_file("foo/bar.txt", b"bar")
        write_file("foo/bar/baz.txt", b"baz")
        copy_test_resource("bitcoin.pdf")
        copy_test_resource("small.png")
        copy_test_resource("test.txt")

        # Add some empty directories
        mkdir("foo-empty")
        mkdir("foo/bar-empty")
        mkdir("foo/bar/baz-empty")

        return bucket

    @pytest.fixture()
    def driver(self, session, bucket):
        return AmazonS3FileManagerDriver(session=session, bucket=bucket)

    @pytest.fixture()
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture()
    def get_s3_value(self, s3_client, bucket):
        def _get_s3_value(key):
            return s3_client.get_object(Bucket=bucket, Key=key)["Body"].read().decode()

        return _get_s3_value

    @pytest.mark.parametrize("workdir", ["", ".", "foo", "foo/bar"])
    def test_validate_workdir(self, workdir, session, bucket):
        with pytest.raises(ValueError):
            AmazonS3FileManagerDriver(session=session, bucket=bucket, workdir=workdir)

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
    def test_list_files(self, workdir, path, expected, driver):
        driver.workdir = workdir

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
    def test_list_files_failure(self, workdir, path, expected, driver):
        driver.workdir = workdir

        with pytest.raises(expected):
            driver.list_files(path)

    def test_load_file(self, driver):
        artifact = driver.load_file("resources/bitcoin.pdf")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 4

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # non-existent files or directories
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
    def test_load_file_failure(self, workdir, path, expected, driver):
        driver.workdir = workdir

        with pytest.raises(expected):
            driver.load_file(path)

    def test_load_file_with_encoding(self, driver):
        artifact = driver.load_file("resources/test.txt")

        assert isinstance(artifact, ListArtifact)
        assert len(artifact.value) == 1
        assert isinstance(artifact.value[0], TextArtifact)

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
    def test_save_file(self, workdir, path, content, driver, get_s3_value):
        driver.workdir = workdir

        result = driver.save_file(path, content)

        assert isinstance(result, InfoArtifact)
        assert result.value == "Successfully saved file"
        expected_s3_key = f"{workdir}/{path}".lstrip("/")
        content_str = content if isinstance(content, str) else content.decode()
        assert get_s3_value(expected_s3_key) == content_str

    @pytest.mark.parametrize(
        ("workdir", "path", "expected"),
        [
            # non-existent directories
            ("/", "bar/", IsADirectoryError),
            ("/", "/bar/", IsADirectoryError),
            # # existing directories
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
    def test_save_file_failure(self, workdir, path, expected, temp_dir, driver, s3_client, bucket):
        driver.workdir = workdir

        with pytest.raises(expected):
            driver.save_file(path, "foobar")

    def test_save_file_with_encoding(self, session, bucket, get_s3_value):
        workdir = "/sub-folder"
        driver = AmazonS3FileManagerDriver(
            session=session, bucket=bucket, default_loader=TextLoader(encoding="utf-8"), loaders={}, workdir=workdir
        )
        path = "test/foobar.txt"

        result = driver.save_file(path, "foobar")

        expected_s3_key = f"{workdir}/{path}".lstrip("/")
        assert get_s3_value(expected_s3_key) == "foobar"
        assert result.value == "Successfully saved file"

    def test_save_and_load_file_with_encoding(self, session, bucket, get_s3_value):
        workdir = "/sub-folder"
        driver = AmazonS3FileManagerDriver(
            session=session, bucket=bucket, loaders={"txt": TextLoader(encoding="ascii")}, workdir=workdir
        )
        path = "test/foobar.txt"

        result = driver.save_file(path, "foobar")

        expected_s3_key = f"{workdir}/{path}".lstrip("/")
        assert get_s3_value(expected_s3_key) == "foobar"
        assert result.value == "Successfully saved file"

        driver = AmazonS3FileManagerDriver(
            session=session, bucket=bucket, default_loader=TextLoader(encoding="ascii"), loaders={}, workdir=workdir
        )
        path = "test/foobar.txt"

        result = driver.load_file(path)

        assert isinstance(result, ListArtifact)
        assert len(result.value) == 1
        assert isinstance(result.value[0], TextArtifact)
