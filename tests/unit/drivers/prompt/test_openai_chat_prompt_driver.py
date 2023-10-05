from griptape.drivers import OpenAiChatPromptDriver
from griptape.utils import PromptStack
from griptape.tokenizers import OpenAiTokenizer
from unittest.mock import ANY, Mock
import pytest

class TestOpenAiChatPromptDriverFixtureMixin:
    @pytest.fixture(autouse=True)
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch('openai.ChatCompletion').create
        mock_chat_create.return_value.choices = [ 
            {'message': {'content': 'model-output'}}
        ]
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
    def messages(self):
        return [
            {'role': 'user', 'content': 'generic-input'},
            {'role': 'system', 'content': 'system-input'},
            {'role': 'user', 'content': 'user-input'},
            {'role': 'assistant', 'content': 'assistant-input'},
        ]

class TestOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL,
        )

    def test_try_run(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            user=driver.user,
            api_key=driver.api_key,
            organization=driver.organization,
            api_version=driver.api_version,
            api_base=driver.api_base,
            api_type=driver.api_type,
            messages=messages
        )
        assert text_artifact.value == 'model-output'

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
        )

        # When
        with pytest.raises(Exception) as e:
            driver.try_run('prompt-stack')

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"

    @pytest.mark.parametrize('choices', [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(self, choices, mock_chat_completion_create, prompt_stack):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
        mock_chat_completion_create.return_value.choices = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[0] == 'Completion with more than one choice is not supported yet.'

    def test_token_count(self, prompt_stack, messages):
        # Given
        mock_tokenizer = Mock()
        mock_tokenizer.token_count.return_value = 42
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, tokenizer=mock_tokenizer)
        
        # When
        token_count = driver.token_count(prompt_stack)

        # Then
        mock_tokenizer.token_count.assert_called_once_with(messages)
        assert token_count == 42

    def test_max_output_tokens(self, messages):
        # Given
        mock_tokenizer = Mock()
        mock_tokenizer.tokens_left.return_value = 42
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, tokenizer=mock_tokenizer)
        
        # When
        max_output_tokens = driver.max_output_tokens(messages)

        # Then
        mock_tokenizer.tokens_left.assert_called_once_with(messages)
        assert max_output_tokens == 42

    def test_max_output_tokens_with_max_tokens(self, messages):
        OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, max_tokens=42).max_output_tokens(messages) == 42
