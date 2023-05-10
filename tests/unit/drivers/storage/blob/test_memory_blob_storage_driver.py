import pytest
from griptape.artifacts import BlobArtifact
from griptape.drivers import MemoryBlobStorageDriver


class TestMemoryBlobStorageDriver:
    @pytest.fixture
    def driver(self):
        return MemoryBlobStorageDriver()

    def test_save(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        key = driver.save(artifact)

        assert driver.load(key) == artifact

    def test_load(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        key = driver.save(artifact)

        assert driver.load(key) == artifact
        assert driver.load("empty") is None

    def test_delete(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        key = driver.save(artifact)

        driver.delete(key)

        assert driver.load(key) is None
        assert driver.delete(key) is None
