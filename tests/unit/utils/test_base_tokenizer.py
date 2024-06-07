from griptape.common import PromptStack
from tests.mocks.mock_tokenizer import MockTokenizer


class TestBaseTokenizer:
    def test_token_count(self):
        assert (
            MockTokenizer(model="foo bar").count_tokens(
                PromptStack(inputs=[PromptStack.Input("foobar", role=PromptStack.USER_ROLE)])
            )
            == 24
        )

    def test_prompt_stack_to_string(self):
        assert (
            MockTokenizer(model="foo bar").prompt_stack_to_string(
                PromptStack(inputs=[PromptStack.Input("foobar", role=PromptStack.USER_ROLE)])
            )
            == "User: foobar\n\nAssistant:"
        )
