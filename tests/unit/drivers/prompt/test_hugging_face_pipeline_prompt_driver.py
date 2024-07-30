import pytest

from griptape.common import PromptStack
from griptape.drivers import HuggingFacePipelinePromptDriver


class TestHuggingFacePipelinePromptDriver:
    @pytest.fixture(autouse=True)
    def mock_pipeline(self, mocker):
        mock_pipeline = mocker.patch("transformers.pipeline")
        return mock_pipeline

    @pytest.fixture(autouse=True)
    def mock_generator(self, mock_pipeline):
        mock_generator = mock_pipeline.return_value
        mock_generator.task = "text-generation"
        mock_generator.return_value = [{"generated_text": [{"content": "model-output"}]}]
        return mock_generator

    @pytest.fixture(autouse=True)
    def mock_autotokenizer(self, mocker):
        mock_autotokenizer = mocker.patch("transformers.AutoTokenizer.from_pretrained").return_value
        mock_autotokenizer.model_max_length = 42
        mock_autotokenizer.apply_chat_template.return_value = [1, 2, 3]
        mock_autotokenizer.decode.return_value = "model-output"
        mock_autotokenizer.encode.return_value = [1, 2, 3]
        return mock_autotokenizer

    @pytest.fixture()
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_assistant_message("assistant-input")
        return prompt_stack

    def test_init(self):
        assert HuggingFacePipelinePromptDriver(model="gpt2", max_tokens=42)

    def test_try_run(self, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)

        # When
        message = driver.try_run(prompt_stack)

        # Then
        assert message.value == "model-output"
        assert message.usage.input_tokens == 3
        assert message.usage.output_tokens == 3

    def test_try_stream(self, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)

        # When
        with pytest.raises(Exception) as e:
            driver.try_stream(prompt_stack)

        assert e.value.args[0] == "streaming is not supported"

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_generator, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)
        mock_generator.return_value = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "completion with more than one choice is not supported yet"

    def test_try_run_throws_when_non_list(self, mock_generator, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)
        mock_generator.return_value = {}

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "invalid output format"

    def test_prompt_stack_to_string(self, prompt_stack):
        # Given
        driver = HuggingFacePipelinePromptDriver(model="foo", max_tokens=42)

        # When
        result = driver.prompt_stack_to_string(prompt_stack)

        # Then
        assert result == "model-output"
