import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import DummyImageQueryDriver
from griptape.exceptions import DummyError


class TestDummyImageQueryDriver:
    @pytest.fixture()
    def image_query_driver(self):
        return DummyImageQueryDriver()

    def test_init(self, image_query_driver):
        assert image_query_driver

    def test_try_query(self, image_query_driver):
        with pytest.raises(DummyError):
            image_query_driver.try_query("Prompt", [ImageArtifact(value=b"", width=100, height=100, format="png")])
