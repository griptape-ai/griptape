from unittest import mock
import json
import boto3
import pytest
from griptape.tokenizers import BedrockLlamaTokenizer
from griptape.utils import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver, BedrockLlamaPromptModelDriver


class TestBedrockLlamaPromptModelDriver:
    @pytest.fixture(autouse=True)
    def mock_session(self, mocker):
        fake_tokenization = '{"generation_token_count": 13}'
        mock_session_class = mocker.patch("boto3.Session")

        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_response = mock.Mock()

        mock_response.get().read.return_value = fake_tokenization
        mock_client.invoke_model.return_value = mock_response
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

        return mock_session_object

    @pytest.fixture
    def driver(self):
        return AmazonBedrockPromptDriver(
            model=BedrockLlamaTokenizer.DEFAULT_MODEL,
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockLlamaPromptModelDriver(),
            temperature=0.12345,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")
        stack.add_assistant_input("baz")
        stack.add_user_input("qux")

        return stack

    def test_init(self, driver):
        assert driver.prompt_driver is not None

    def test_prompt_stack_to_model_input(self, driver, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, str)
        assert model_input == "<s>[INST] <<SYS>>\nfoo\n<</SYS>>\n\nbar [/INST]baz </s><s>[INST] qux [/INST]"

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_gen_length"] == 4091
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver):
        assert driver.process_output(json.dumps({"generation": "foobar"})).value == "foobar"
