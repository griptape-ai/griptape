from griptape.drivers import DummyImageQueryDriver
from griptape.artifacts import ImageArtifact
import pytest

from griptape.exceptions import DummyException


class TestDummyImageQueryDriver:
    @pytest.fixture
    def image_query_driver(self):
        return DummyImageQueryDriver()

    def test_init(self, image_query_driver):
        assert image_query_driver

    def test_try_query(self, image_query_driver):
        with pytest.raises(DummyException):
            image_query_driver.try_query("Prompt", [ImageArtifact(value=b"", width=100, height=100)])
