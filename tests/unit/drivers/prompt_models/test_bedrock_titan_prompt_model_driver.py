import json
import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonBedrockPromptDriver, BedrockTitanPromptModelDriver

class TestBedrockTitanPromptModelDriver:
    @pytest.fixture
    def driver(self):
        return AmazonBedrockPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=BedrockTitanPromptModelDriver(),
            temperature=0.12345,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_prompt_stack_to_model_input(self, driver, stack):
        model_input = driver.prompt_stack_to_model_input(stack)

        assert isinstance(model_input, dict)
        assert model_input['inputText'].startswith("User: foo\nUser: bar\n\nBot:")

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["textGenerationConfig"]["maxTokenCount"] == 4083
        assert driver.prompt_stack_to_model_params(stack)["textGenerationConfig"]["temperature"] == 0.12345

    def test_process_output(self, driver):
        assert (
            driver.process_output(
                json.dumps({"results": [{"outputText": "foobar"}]})
            ).value
            == "foobar"
        )
