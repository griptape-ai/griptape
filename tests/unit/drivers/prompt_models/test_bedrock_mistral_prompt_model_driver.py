from unittest import mock
import json
import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver, BedrockMistralPromptModelDriver


class TestBedrockMistralPromptModelDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

        return mock_session_object

    @pytest.fixture
    def driver(self):
        return AmazonBedrockPromptDriver(
            model="mistral.mistral-7b-instruct-v0:2",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockMistralPromptModelDriver(top_p=0.9, top_k=250),
            temperature=0.12345,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("system-input")
        stack.add_user_input("user-input")
        stack.add_assistant_input("assistant-input")
        stack.add_user_input("user-input")

        return stack

    def test_init(self, driver):
        assert driver.prompt_driver is not None

    def test_prompt_stack_to_model_input(self, driver, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, str)
        assert model_input == "<s>[INST] system-input user-input [/INST]assistant-input</s> [INST] user-input [/INST]"

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_tokens"] == 8177
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345
        assert driver.prompt_stack_to_model_params(stack)["top_p"] == 0.9
        assert driver.prompt_stack_to_model_params(stack)["top_k"] == 250

    def test_process_output(self, driver):
        assert driver.process_output(json.dumps({"outputs": [{"text": "foobar", "stop": "reason"}]})).value == "foobar"
