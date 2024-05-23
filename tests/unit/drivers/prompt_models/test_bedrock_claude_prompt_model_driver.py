from unittest import mock
import json
import boto3
import pytest
from griptape.common import PromptStack
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

    @pytest.mark.parametrize(
        "driver,",
        [
            ("anthropic.claude-v2"),
            ("anthropic.claude-v2:1"),
            ("anthropic.claude-3-sonnet-20240229-v1:0"),
            ("anthropic.claude-3-haiku-20240307-v1:0"),
        ],
        indirect=["driver"],
    )
    def test_init(self, driver):
        assert driver.prompt_driver is not None

    @pytest.mark.parametrize(
        "driver,",
        [
            ("anthropic.claude-v2"),
            ("anthropic.claude-v2:1"),
            ("anthropic.claude-3-sonnet-20240229-v1:0"),
            ("anthropic.claude-3-haiku-20240307-v1:0"),
        ],
        indirect=["driver"],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_prompt_stack_to_model_input(self, driver, system_enabled):
        stack = PromptStack()
        if system_enabled:
            stack.add_system_input("foo")
        stack.add_user_input("bar")
        stack.add_assistant_input("baz")
        stack.add_generic_input("qux")

        expected_messages = [
            {"role": "user", "content": "bar"},
            {"role": "assistant", "content": "baz"},
            {"role": "user", "content": "qux"},
        ]
        actual = driver.prompt_stack_to_model_input(stack)
        expected = {"messages": expected_messages, **({"system": "foo"} if system_enabled else {})}

        assert actual == expected

    @pytest.mark.parametrize(
        "driver,",
        [
            ("anthropic.claude-v2"),
            ("anthropic.claude-v2:1"),
            ("anthropic.claude-3-sonnet-20240229-v1:0"),
            ("anthropic.claude-3-haiku-20240307-v1:0"),
        ],
        indirect=["driver"],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_prompt_stack_to_model_params(self, driver, system_enabled):
        stack = PromptStack()
        if system_enabled:
            stack.add_system_input("foo")
        stack.add_user_input("bar")
        stack.add_assistant_input("baz")
        stack.add_generic_input("qux")

        max_tokens = driver.prompt_driver.max_output_tokens(driver.prompt_driver.prompt_stack_to_string(stack))

        expected = {
            "temperature": 0.12345,
            "max_tokens": max_tokens,
            "anthropic_version": driver.ANTHROPIC_VERSION,
            "messages": [
                {"role": "user", "content": "bar"},
                {"role": "assistant", "content": "baz"},
                {"role": "user", "content": "qux"},
            ],
            "top_p": 0.999,
            "top_k": 250,
            "stop_sequences": ["<|Response|>"],
            **({"system": "foo"} if system_enabled else {}),
        }

        assert driver.prompt_stack_to_model_params(stack) == expected

    @pytest.mark.parametrize(
        "driver,",
        [
            ("anthropic.claude-v2"),
            ("anthropic.claude-v2:1"),
            ("anthropic.claude-3-sonnet-20240229-v1:0"),
            ("anthropic.claude-3-haiku-20240307-v1:0"),
        ],
        indirect=["driver"],
    )
    def test_process_output(self, driver):
        assert (
            driver.process_output(json.dumps({"type": "message", "content": [{"text": "foobar"}]}).encode()).value
            == "foobar"
        )
        assert (
            driver.process_output(
                json.dumps({"type": "content_block_delta", "delta": {"text": "foobar"}}).encode()
            ).value
            == "foobar"
        )
