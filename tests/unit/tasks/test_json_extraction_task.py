from griptape.engines import JsonExtractionEngine
import pytest
from schema import Schema
from griptape.structures import Agent
from griptape.tasks import JsonExtractionTask
from tests.mocks.mock_structure_config import MockStructureConfig
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestJsonExtractionTask:
    @pytest.fixture
    def task(self):
        return JsonExtractionTask("foo", args={"template_schema": Schema({"foo": "bar"}).json_schema("TemplateSchema")})

    def test_run(self, task):
        mock_config = MockStructureConfig()
        assert isinstance(mock_config.global_drivers.prompt_driver, MockPromptDriver)
        mock_config.global_drivers.prompt_driver.mock_output = (
            '[{"test_key_1": "test_value_1"}, {"test_key_2": "test_value_2"}]'
        )
        agent = Agent(config=mock_config)

        agent.add_task(task)

        result = task.run()

        assert len(result.value) == 2
        assert result.value[0].value == "{'test_key_1': 'test_value_1'}"
        assert result.value[1].value == "{'test_key_2': 'test_value_2'}"

    def test_config_extraction_engine(self, task):
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.extraction_engine, JsonExtractionEngine)
        assert isinstance(task.extraction_engine.prompt_driver, MockPromptDriver)

    def test_missing_extraction_engine(self, task):
        with pytest.raises(ValueError):
            task.extraction_engine
