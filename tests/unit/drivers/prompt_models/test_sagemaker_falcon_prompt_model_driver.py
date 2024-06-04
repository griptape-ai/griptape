import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonSageMakerPromptDriver, SageMakerFalconPromptModelDriver


class TestSageMakerFalconPromptModelDriver:
    @pytest.fixture(autouse=True)
    def tokenizer(self, mocker):
        from_pretrained = tokenizer = mocker.patch("transformers.AutoTokenizer").from_pretrained
        from_pretrained.return_value.apply_chat_template.return_value = [1, 2, 3]
        from_pretrained.return_value.decode.return_value = "foo\n\nUser: bar"
        from_pretrained.return_value.model_max_length = 8000

        return tokenizer

    @pytest.fixture
    def driver(self):
        return AmazonSageMakerPromptDriver(
            endpoint="endpoint-name",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=SageMakerFalconPromptModelDriver(),
            temperature=0.12345,
            max_tokens=590,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_init(self, driver):
        assert driver.prompt_driver is not None

    def test_prompt_stack_to_model_input(self, driver, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, str)
        assert model_input.startswith("foo\n\nUser: bar")

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_new_tokens"] == 590
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver, stack):
        assert driver.process_output([{"generated_text": "foobar"}]).value == "foobar"

    def test_tokenizer_max_model_length(self, driver):
        assert driver.tokenizer.tokenizer.model_max_length == 8000
