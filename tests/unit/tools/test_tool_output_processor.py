import pytest
from griptape.artifacts import TextArtifact, CsvRowArtifact, BaseArtifact, ListArtifact
from griptape.tools import ToolOutputProcessor
from tests.utils import defaults


class TestTextMemoryBrowser:
    @pytest.fixture(autouse=True)
    def mock_griptape(self, mocker):
        mocker.patch(
            "griptape.engines.VectorQueryEngine.query",
            return_value=TextArtifact("foobar")
        )

        mocker.patch(
            "griptape.engines.PromptSummaryEngine.summarize_artifacts",
            return_value=TextArtifact("foobar summary")
        )

        mocker.patch(
            "griptape.engines.CsvExtractionEngine.extract",
            return_value=ListArtifact([CsvRowArtifact({"foo": "bar"})])
        )

        mocker.patch(
            "griptape.engines.JsonExtractionEngine.extract",
            return_value=ListArtifact([TextArtifact('{"foo":"bar"}')])
        )

    @pytest.fixture
    def tool(self):
        return ToolOutputProcessor(
            input_memory=[
                defaults.text_tool_memory("Memory1")
            ]
        )

    def test_insert(self, tool):
        tool.insert(
            {"values": {"memory_name": tool.input_memory[0].name, "artifact_namespace": "foo", "text": "foobar"}}
        )

        assert BaseArtifact.from_json(
            tool.input_memory[0].query_engine.vector_store_driver.load_entries("foo")[0].meta["artifact"]
        ).value == "foobar"

    def test_summarize(self, tool):
        assert tool.summarize(
            {"values": {"memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}
        ).value == "foobar summary"

    def test_query(self, tool):
        assert tool.search(
            {"values": {"query": "foobar", "memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}
        ).value == "foobar"

    def test_extract_csv_rows(self, tool):
        assert tool.extract_csv_rows(
            {"values": {"column_names": "foo", "memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}
        ).value[0].value == {"foo": "bar"}

    def test_extract_json_objects(self, tool):
        assert tool.extract_json_objects(
            {"values": {"json_schema": {}, "memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}
        ).value[0].value == '{"foo":"bar"}'
