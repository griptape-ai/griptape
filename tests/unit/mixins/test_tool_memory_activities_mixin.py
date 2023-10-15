import pytest
from griptape.artifacts import TextArtifact, CsvRowArtifact, ListArtifact
from tests.mocks.mock_text_memory_processor import MockToolMemoryProcessor


class TestToolMemoryActivitiesMixin:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.engines.CsvExtractionEngine.extract",
            return_value=ListArtifact([CsvRowArtifact({"foo": "bar"})])
        )

        mocker.patch(
            "griptape.engines.JsonExtractionEngine.extract",
            return_value=ListArtifact([TextArtifact("foobar")])
        )

    @pytest.fixture
    def processor(self):
        return MockToolMemoryProcessor()

    def test_summarize(self, processor):
        processor.memory.store_artifact("foo", TextArtifact("test"))

        assert processor.summarize(
            {"values": {"memory_name": processor.memory.name, "artifact_namespace": "foo"}}
        ).value == "mock output"

    def test_search(self, processor):
        assert processor.search(
            {"values": {"query": "foobar", "memory_name": processor.memory.name, "artifact_namespace": "foo"}}
        ).value == "foobar"

    def test_extract_csv_rows(self, processor):
        assert processor.extract_csv_rows(
            {"values": {"column_names": ["foo"], "memory_name": processor.memory.name, "artifact_namespace": "foo"}}
        ).value[0].value == {"foo": "bar"}

    def test_extract_json_objects(self, processor):
        assert processor.extract_json_objects(
            {"values": {"json_schema": "{}", "memory_name": processor.memory.name, "artifact_namespace": "foo"}}
        ).value[0].value == "foobar"
