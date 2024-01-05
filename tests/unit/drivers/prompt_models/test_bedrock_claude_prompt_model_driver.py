from unittest import mock
import json
import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver, BedrockClaudePromptModelDriver


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
            prompt_model_driver=BedrockClaudePromptModelDriver(),
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

    @pytest.mark.parametrize("driver", [("anthropic.claude-v2:1"), ("anthropic.claude-v2")], indirect=["driver"])
    def test_init(self, driver):
        assert driver.prompt_driver is not None

    @pytest.mark.parametrize(
        "driver,expected",
        [
            ("anthropic.claude-v2:1", "foo\n\nHuman: bar\n\nAssistant: baz\n\nHuman: qux\n\nAssistant:"),
            (
                "anthropic.claude-v2",
                "\n\nHuman: foo\n\nAssistant:\n\nHuman: bar\n\nAssistant: baz\n\nHuman: qux\n\nAssistant:",
            ),
        ],
        indirect=["driver"],
    )
    def test_prompt_stack_to_model_input(self, driver, expected, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, dict)
        assert model_input["prompt"].startswith(expected)

    @pytest.mark.parametrize(
        "driver,key,expected",
        [
            ("anthropic.claude-v2:1", "max_tokens_to_sample", 199979),
            ("anthropic.claude-v2", "max_tokens_to_sample", 99971),
            ("anthropic.claude-v2:1", "temperature", 0.12345),
            ("anthropic.claude-v2", "temperature", 0.12345),
        ],
        indirect=["driver"],
    )
    def test_prompt_stack_to_model_params(self, driver, key, expected, stack):
        assert driver.prompt_stack_to_model_params(stack)[key] == expected

    @pytest.mark.parametrize(
        "driver,expected", [("anthropic.claude-v2:1", "foobar"), ("anthropic.claude-v2", "foobar")], indirect=["driver"]
    )
    def test_process_output(self, driver, expected):
        assert driver.process_output(json.dumps({"completion": "foobar"}).encode()).value == expected
