import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonSageMakerPromptDriver, SageMakerLlamaPromptModelDriver


class TestSageMakerLlamaPromptModelDriver:
    @pytest.fixture(autouse=True)
    def llama3_instruct_tokenizer(self, mocker):
        tokenizer = mocker.patch("transformers.AutoTokenizer").return_value
        tokenizer.model_max_length = 8000

        return tokenizer

    @pytest.fixture(autouse=True)
    def hugging_face_tokenizer(self, mocker, llama3_instruct_tokenizer):
        tokenizer = mocker.patch(
            "griptape.drivers.prompt_model.sagemaker_llama_prompt_model_driver.HuggingFaceTokenizer"
        ).return_value
        tokenizer.count_output_tokens_left.return_value = 7991
        tokenizer.tokenizer = llama3_instruct_tokenizer
        return tokenizer

    @pytest.fixture
    def driver(self):
        return AmazonSageMakerPromptDriver(
            endpoint="endpoint-name",
            model="inference-component-name",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=SageMakerLlamaPromptModelDriver(),
            temperature=0.12345,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_init(self, driver):
        assert driver.prompt_driver is not None

    def test_prompt_stack_to_model_input(self, driver, stack, hugging_face_tokenizer):
        driver.prompt_stack_to_model_input(stack)

        hugging_face_tokenizer.tokenizer.apply_chat_template.assert_called_once_with(
            [{"role": "system", "content": "foo"}, {"role": "user", "content": "bar"}],
            tokenize=False,
            add_generation_prompt=True,
        )

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_new_tokens"] == 7991
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver, stack):
        assert driver.process_output({"generated_text": "foobar"}).value == "foobar"

    def test_process_output_invalid_format(self, driver, stack):
        with pytest.raises(ValueError):
            assert driver.process_output([{"generated_text": "foobar"}])

    def test_tokenizer_max_model_length(self, driver):
        assert driver.tokenizer.tokenizer.model_max_length == 8000
