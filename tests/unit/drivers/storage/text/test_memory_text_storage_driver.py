import pytest
from griptape.drivers import MemoryTextStorageDriver


class TestMemoryTextStorageDriver:
    @pytest.fixture
    def driver(self):
        return MemoryTextStorageDriver()

    def test_save(self, driver):
        key = driver.save("foo")

        assert driver.load(key) == "foo"

    def test_load(self, driver):
        key = driver.save("foo")

        assert driver.load(key) == "foo"
        assert driver.load("empty") is None

    def test_delete(self, driver):
        key = driver.save("foo")

        driver.delete(key)

        assert driver.load(key) is None
        assert driver.delete(key) is None
