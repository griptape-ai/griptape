import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers.parser.pillow_parser_driver import PillowParserDriver


class TestPillowParserDriver:
    @pytest.fixture()
    def driver(self):
        return PillowParserDriver()

    @pytest.fixture(params=["bytes_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        ("resource_path", "mime_type"),
        [
            ("small.png", "image/png"),
            ("small.jpg", "image/jpeg"),
            ("small.webp", "image/webp"),
            ("small.bmp", "image/bmp"),
            ("small.gif", "image/gif"),
            ("small.tiff", "image/tiff"),
        ],
    )
    def test_parse(self, resource_path, mime_type, driver, create_source):
        source = create_source(resource_path).read()

        artifact = driver.parse(source)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == mime_type
        assert len(artifact.value) > 0
