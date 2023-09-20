import json
import pytest
from schema import Schema
from griptape.artifacts import TextArtifact
from griptape.engines import JsonExtractionEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestJsonExtractionEngine:
    @pytest.fixture
    def engine(self):
        return JsonExtractionEngine(
            prompt_driver=MockPromptDriver(
                mock_output='[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]'
            )
        )

    def test_extract(self, engine):
        json_schema = json.dumps(Schema({"foo": "bar"}).json_schema("TemplateSchema"))
        result = engine.extract([TextArtifact("foo")], json_schema)

        assert result[0].value == "{'test_key_1': 'test_value_1'}"
        assert result[1].value == "{'test_key_2': 'test_value_2'}"

    def test_extract_with_non_json_schema(self, engine):
        with pytest.raises(ValueError):
            engine.extract([TextArtifact("foo")], "non json")

    def test_json_to_text_artifacts(self, engine):
        assert [a.value for a in engine.json_to_text_artifacts('["foo", "bar"]')] == ["foo", "bar"]
        