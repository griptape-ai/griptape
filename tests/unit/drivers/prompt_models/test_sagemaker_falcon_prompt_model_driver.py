import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonSagemakerPromptDriver, SagemakerFalconPromptModelDriver
from griptape.tokenizers import TiktokenTokenizer


class TestSagemakerFalconPromptModelDriver:
    @pytest.fixture
    def driver(self):
        return AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_driver_class=SagemakerFalconPromptModelDriver,
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

        assert isinstance(model_input, str)
        assert model_input.startswith("foo\n\nUser: bar")

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_new_tokens"] == 4083
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver, stack):
        assert driver.process_output([
            {"generated_text": "foobar"}
        ]).value == "foobar"
