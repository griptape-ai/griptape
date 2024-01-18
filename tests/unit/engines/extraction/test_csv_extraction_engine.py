import pytest
from griptape.engines import CsvExtractionEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestCsvExtractionEngine:
    @pytest.fixture
    def engine(self):
        return CsvExtractionEngine(prompt_driver=MockPromptDriver())

    def test_extract(self, engine):
        result = engine.extract("foo", column_names=["test1"])

        assert len(result.value) == 1
        assert result.value[0].value == {"test1": "mock output"}

    def test_text_to_csv_rows(self, engine):
        result = engine.text_to_csv_rows("foo,bar\nbaz,maz", ["test1", "test2"])

        assert len(result) == 2
        assert result[0].value == {"test1": "foo", "test2": "bar"}
        assert result[1].value == {"test1": "baz", "test2": "maz"}
