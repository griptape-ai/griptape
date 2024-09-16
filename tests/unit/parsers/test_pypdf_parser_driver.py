import pytest

from griptape.drivers.parser.pypdf_parser_driver import PyPdfParserDriver


class TestPyPdfParserDriver:
    @pytest.fixture()
    def driver(self):
        return PyPdfParserDriver()

    @pytest.fixture(params=["bytes_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_parse(self, driver, create_source):
        source = create_source("bitcoin.pdf").read()

        artifact = driver.parse(source)

        assert len(artifact) == 9
        assert artifact[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifact[-1].value.endswith('its applications," 1957.\n9')
