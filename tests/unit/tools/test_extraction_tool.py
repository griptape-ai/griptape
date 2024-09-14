import json

import pytest

from griptape.artifacts import TextArtifact
from griptape.engines import CsvExtractionEngine, JsonExtractionEngine
from griptape.tools import ExtractionTool
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils import defaults


class TestExtractionTool:
    @pytest.fixture()
    def json_tool(self):
        return ExtractionTool(
            input_memory=[defaults.text_task_memory("TestMemory")],
            extraction_engine=JsonExtractionEngine(
                prompt_driver=MockPromptDriver(
                    mock_output='[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]'
                ),
                template_schema={},
            ),
        )

    @pytest.fixture()
    def csv_tool(self):
        return ExtractionTool(
            input_memory=[defaults.text_task_memory("TestMemory")],
            extraction_engine=CsvExtractionEngine(
                prompt_driver=MockPromptDriver(),
                column_names=["test1"],
            ),
        )

    def test_json_extract_artifacts(self, json_tool):
        json_tool.input_memory[0].store_artifact("foo", TextArtifact(json.dumps({})))

        result = json_tool.extract(
            {"values": {"data": {"memory_name": json_tool.input_memory[0].name, "artifact_namespace": "foo"}}}
        )

        assert len(result.value) == 2
        assert result.value[0].value == {"test_key_1": "test_value_1"}
        assert result.value[1].value == {"test_key_2": "test_value_2"}

    def test_json_extract_content(self, json_tool):
        result = json_tool.extract({"values": {"data": "foo"}})

        assert len(result.value) == 2
        assert result.value[0].value == {"test_key_1": "test_value_1"}
        assert result.value[1].value == {"test_key_2": "test_value_2"}

    def test_csv_extract_artifacts(self, csv_tool):
        csv_tool.input_memory[0].store_artifact("foo", TextArtifact("foo,bar\nbaz,maz"))

        result = csv_tool.extract(
            {"values": {"data": {"memory_name": csv_tool.input_memory[0].name, "artifact_namespace": "foo"}}}
        )

        assert len(result.value) == 1
        assert result.value[0].value == "test1: mock output"

    def test_csv_extract_content(self, csv_tool):
        result = csv_tool.extract({"values": {"data": "foo"}})

        assert len(result.value) == 1
        assert result.value[0].value == "test1: mock output"
