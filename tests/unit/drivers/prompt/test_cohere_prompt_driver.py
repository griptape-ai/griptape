from griptape.drivers import CoherePromptDriver
from griptape.utils import PromptStack
from unittest.mock import Mock
import pytest


class TestCoherePromptDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch('cohere.Client').return_value
        mock_client.generate.return_value.generations = [Mock()]
        mock_client.generate.return_value.generations[0].text = 'model-output'
        return mock_client
    
    @pytest.fixture(autouse=True)
    def mock_tokenizer(self, mocker):
        return mocker.patch('griptape.tokenizers.CohereTokenizer').return_value
    
    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input('generic-input')
        prompt_stack.add_system_input('system-input')
        prompt_stack.add_user_input('user-input')
        prompt_stack.add_assistant_input('assistant-input')
        return prompt_stack

    def test_init(self):
        assert CoherePromptDriver(api_key="foobar")

    def test_try_run(self, prompt_stack):
        # Given
        driver = CoherePromptDriver(api_key='api-key')

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        assert text_artifact.value == 'model-output'

    @pytest.mark.parametrize('choices', [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_client, prompt_stack):
        # Given
        driver = CoherePromptDriver(api_key='api-key')
        mock_client.generate.return_value.generations = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == 'Completion with more than one choice is not supported yet.'