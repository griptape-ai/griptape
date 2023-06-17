import pytest
from griptape.artifacts import BlobArtifact
from griptape.drivers import LocalBlobToolMemoryDriver


class TestLocalBlobToolMemoryDriver:
    @pytest.fixture
    def driver(self):
        return LocalBlobToolMemoryDriver()

    def test_save(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        driver.save("test", artifact)

        assert driver.load("test") == [artifact]

    def test_load(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        driver.save("test", artifact)

        assert driver.load("test") == [artifact]
        assert driver.load("empty") == []

    def test_delete(self, driver):
        artifact = BlobArtifact(b"foo", name="foo")
        driver.save("test", artifact)

        driver.delete('test')

        assert driver.load("test") == []
        assert driver.delete("test") is None
