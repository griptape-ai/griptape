import pytest

from griptape.drivers.parser.text_parser_driver import TextParserDriver


class TestTextParserDriver:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def driver(self, request):
        return TextParserDriver(encoding=request.param) if request.param is not None else TextParserDriver()

    @pytest.fixture(params=["bytes_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_parse(self, driver, create_source):
        source = create_source("test.txt").read()

        artifact = driver.parse(source)

        assert artifact.value.startswith("foobar foobar foobar")
        assert artifact.encoding == driver.encoding
