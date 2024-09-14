import pytest

from griptape.engines import CsvExtractionEngine


class TestCsvExtractionEngine:
    @pytest.fixture()
    def engine(self):
        return CsvExtractionEngine(column_names=["test1"])

    def test_extract_text(self, engine):
        result = engine.extract_text("foo")

        assert len(result.value) == 1
        assert result.value[0].value == "test1: mock output"

    def test_text_to_csv_rows(self, engine):
        result = engine.text_to_csv_rows("foo,bar\nbaz,maz", ["test1", "test2"])

        assert len(result) == 2
        assert result[0].value == "test1: foo\ntest2: bar"
        assert result[1].value == "test1: baz\ntest2: maz"
