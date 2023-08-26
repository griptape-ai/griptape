import boto3
import pytest
from griptape.core import PromptStack
from griptape.drivers import AmazonSagemakerPromptDriver, SagemakerLlamaPromptModelDriver
from griptape.tokenizers import TiktokenTokenizer


class TestSagemakerLlamaPromptModelDriver:
    @pytest.fixture
    def driver(self):
        return AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_driver_class=SagemakerLlamaPromptModelDriver,
            temperature=0.12345
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_prompt_stack_to_model_input(self, driver, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, list)
        assert len(model_input[0]) == 2
        assert model_input[0][0]["role"] == "system"
        assert model_input[0][0]["content"] == "foo"
        assert model_input[0][1]["role"] == "user"
        assert model_input[0][1]["content"] == "bar"

    def test_model_params(self, driver, stack):
        assert driver.model_params(stack)["max_new_tokens"] == 4083
        assert driver.model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver, stack):
        assert driver.process_output([
            {"generation": {"content": "foobar"}}
        ]).value == "foobar"
