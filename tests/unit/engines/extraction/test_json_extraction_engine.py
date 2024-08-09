import pytest
from schema import Schema

from griptape.artifacts import ErrorArtifact
from griptape.engines import JsonExtractionEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestJsonExtractionEngine:
    @pytest.fixture()
    def engine(self):
        return JsonExtractionEngine(
            prompt_driver=MockPromptDriver(
                mock_output='[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]'
            ),
            template_schema=Schema({"foo": "bar"}).json_schema("TemplateSchema"),
        )

    def test_extract(self, engine):
        result = engine.extract("foo")

        assert len(result.value) == 2
        assert result.value[0].value == '{"test_key_1": "test_value_1"}'
        assert result.value[1].value == '{"test_key_2": "test_value_2"}'

    def test_extract_error(self, engine):
        engine.template_schema = lambda: "non serializable"
        assert isinstance(engine.extract("foo"), ErrorArtifact)

    def test_json_to_text_artifacts(self, engine):
        assert [
            a.value
            for a in engine.json_to_text_artifacts('[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]')
        ] == ['{"test_key_1": "test_value_1"}', '{"test_key_2": "test_value_2"}']
