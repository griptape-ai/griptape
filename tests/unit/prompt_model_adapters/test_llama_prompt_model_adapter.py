import boto3
import pytest
from griptape.core import PromptStack
from griptape.drivers import AmazonSagemakerPromptDriver
from griptape.prompt_model_adapters import LlamaPromptModelAdapter
from griptape.tokenizers import TiktokenTokenizer


class TestLlamaPromptModelAdapter:
    @pytest.fixture
    def adapter(self):
        return AmazonSagemakerPromptDriver(
            model="foo",
            session=boto3.Session(region_name="us-east-1"),
            tokenizer=TiktokenTokenizer(),
            prompt_model_adapter_class=LlamaPromptModelAdapter,
            temperature=0.12345
        ).prompt_model_adapter

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_prompt_stack_to_model_input(self, adapter, stack):
        model_input = adapter.prompt_stack_to_model_input(stack)

        assert len(model_input) == 2
        assert model_input[0]["role"] == "system"
        assert model_input[0]["content"] == "foo"
        assert model_input[1]["role"] == "user"
        assert model_input[1]["content"] == "bar"

    def test_model_params(self, adapter, stack):
        assert adapter.model_params(stack)["max_new_tokens"] == 4083
        assert adapter.model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, adapter, stack):
        assert adapter.process_output([
            {"generation": {"content": "foobar"}}
        ]).value == "foobar"
