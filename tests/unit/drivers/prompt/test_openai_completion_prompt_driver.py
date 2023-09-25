from griptape.drivers import OpenAiCompletionPromptDriver
from griptape.utils import PromptStack
from unittest.mock import ANY, Mock
import pytest

class TestOpenAiCompletionPromptDriverFixtureMixin:
    @pytest.fixture(autouse=True)
    def mock_completion_create(self, mocker):
        mock_chat_create = mocker.patch('openai.Completion').create
        mock_chat_create.return_value.choices = [  Mock() ]
        mock_chat_create.return_value.choices[0].text = 'model-output'
        return mock_chat_create

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input('generic-input')
        prompt_stack.add_system_input('system-input')
        prompt_stack.add_user_input('user-input')
        prompt_stack.add_assistant_input('assistant-input')
        return prompt_stack

    @pytest.fixture
    def prompt(self):
        return ''.join([
            'generic-input\n\n',
            'system-input\n\n',
            'User: user-input\n\n',
            'Assistant: assistant-input\n\n',
            'Assistant:'
        ])

class TestOpenAiCompletionPromptDriver(TestOpenAiCompletionPromptDriverFixtureMixin):
    def test_init(self):
        assert OpenAiCompletionPromptDriver()

    def test_try_run(self, mock_completion_create, prompt_stack, prompt):
        # Given
        driver = OpenAiCompletionPromptDriver()

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_completion_create.assert_called_once_with(
            model=driver.model,
            max_tokens=ANY,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            prompt=prompt
        )
        assert text_artifact.value == 'model-output'

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        driver = OpenAiCompletionPromptDriver()

        # When
        with pytest.raises(Exception) as e:
            driver.try_run('prompt-stack')

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"

    @pytest.mark.parametrize('choices', [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_completion_create, prompt_stack):
        # Given
        driver = OpenAiCompletionPromptDriver()
        mock_completion_create.return_value.choices = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == 'Completion with more than one choice is not supported yet.'
