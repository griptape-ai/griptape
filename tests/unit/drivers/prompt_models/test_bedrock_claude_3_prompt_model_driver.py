from unittest import mock
import json
import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver, BedrockClaude3PromptModelDriver


class TestBedrockClaudePromptModelDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()

        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

    @pytest.fixture
    def driver(self, request):
        return AmazonBedrockPromptDriver(
            model=request.param,
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockClaude3PromptModelDriver(),
            temperature=0.12345,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")
        stack.add_assistant_input("baz")
        stack.add_generic_input("qux")

        return stack

    @pytest.mark.parametrize("driver", [("anthropic.claude-3-sonnet-20240229-v1:0")], indirect=["driver"])
    def test_init(self, driver):
        assert driver.prompt_driver is not None

    @pytest.mark.parametrize(
        "driver,expected",
        [
            (
                "anthropic.claude-3-sonnet-20240229-v1:0",
                ["foo", [{"content": "bar", "role": "user"}, {"content": "baz", "role": "assistant"}]],
            )
        ],
        indirect=["driver"],
    )
    def test_prompt_stack_to_model_input(self, driver, expected, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, list)
        assert model_input == expected

    @pytest.mark.parametrize(
        "driver,key,expected", [("anthropic.claude-3-sonnet-20240229-v1:0", "max_tokens", 199997)], indirect=["driver"]
    )
    def test_prompt_stack_to_model_params(self, driver, key, expected, stack):
        assert driver.prompt_stack_to_model_params(stack)[key] == expected

    @pytest.mark.parametrize("driver,expected", [("anthropic.claude-v2:1", "foobar")], indirect=["driver"])
    def test_process_output(self, driver, expected):
        assert driver.process_output(b'{ "content": [ { "text": "foobar" } ] }').value == expected
