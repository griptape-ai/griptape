import pytest

from griptape.engines import CsvExtractionEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestCsvExtractionEngine:
    @pytest.fixture()
    def engine(self):
        return CsvExtractionEngine(
            column_names=["header"], prompt_driver=MockPromptDriver(mock_output="header\nmock output")
        )

    def test_extract_text(self, engine):
        result = engine.extract_text("mock output")

        assert len(result.value) == 2
        assert result.value[0].value == "header"
        assert result.value[1].value == "mock output"

    def test_text_to_csv_rows(self, engine):
        result = engine.text_to_csv_rows("key,value\nfoo,bar\nbaz,maz")

        assert len(result) == 2
        assert result[0].value == "foo,bar"
        assert result[1].value == "baz,maz"
