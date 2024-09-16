import pytest

from griptape.drivers.parser.csv_parser_driver import CsvParserDriver


class TestCsvParserDriver:
    @pytest.fixture()
    def driver(self):
        return CsvParserDriver()

    @pytest.fixture()
    def driver_with_pipe_delimiter(self):
        return CsvParserDriver(delimiter="|")

    @pytest.fixture(params=["bytes_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_parse(self, driver, create_source):
        source = create_source("test-1.csv").read()

        artifacts = driver.parse(source)

        assert len(artifacts) == 10
        first_artifact = artifacts[0]
        assert first_artifact.value == "Foo: foo1\nBar: bar1"

    def test_parse_delimiter(self, driver_with_pipe_delimiter, create_source):
        source = create_source("test-pipe.csv").read()

        artifacts = driver_with_pipe_delimiter.parse(source)

        assert len(artifacts) == 10
        first_artifact = artifacts[0]
        assert first_artifact.value == "Bar: foo1\nFoo: bar1"
