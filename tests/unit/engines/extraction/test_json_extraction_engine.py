from os.path import dirname, join, normpath
from pathlib import Path

import pytest
from schema import Schema

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

    def test_extract_text(self, engine):
        result = engine.extract_text("foo")

        assert len(result.value) == 1
        assert result.value[0].value == [{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]

    def test_chunked_extract_text(self, engine):
        large_text = Path(normpath(join(dirname(__file__), "../../../resources", "test.txt"))).read_text()

        extracted = engine.extract_text(large_text * 50)
        assert len(extracted) == 177
        assert extracted[0].value == [{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]

    def test_extract_error(self, engine):
        engine.template_schema = lambda: "non serializable"
        with pytest.raises(TypeError):
            engine.extract_text("foo")

    def test_json_to_text_artifacts(self, engine):
        extracted = engine.json_to_text_artifacts('[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]')
        assert extracted[0].value == [{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]

    def test_json_to_text_artifacts_no_matches(self, engine):
        assert engine.json_to_text_artifacts("asdfasdfasdf") == []
