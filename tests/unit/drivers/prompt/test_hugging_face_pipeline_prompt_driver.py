from griptape.drivers import HuggingFacePipelinePromptDriver
from griptape.common import PromptStack
import pytest


class TestHuggingFacePipelinePromptDriver:
    @pytest.fixture(autouse=True)
    def mock_pipeline(self, mocker):
        mock_pipeline = mocker.patch("transformers.pipeline")
        return mock_pipeline

    @pytest.fixture(autouse=True)
    def mock_generator(self, mock_pipeline):
        mock_generator = mock_pipeline.return_value
        mock_generator.task = "text-generation"
        mock_generator.return_value = [{"generated_text": "model-output"}]
        return mock_generator

    @pytest.fixture(autouse=True)
    def mock_autotokenizer(self, mocker):
        mock_autotokenizer = mocker.patch("transformers.AutoTokenizer.from_pretrained").return_value
        mock_autotokenizer.model_max_length = 42
        return mock_autotokenizer

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        return prompt_stack

    def test_init(self):
        assert HuggingFacePipelinePromptDriver(model="gpt2", max_tokens=42)

    def test_try_run(self, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_generator, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)
        mock_generator.return_value = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == "completion with more than one choice is not supported yet"

    def test_try_run_throws_when_unsupported_task_returned(self, prompt_stack, mock_generator):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)
        mock_generator.task = "obviously-an-unsupported-task"

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0].startswith("only models with the following tasks are supported: ")
