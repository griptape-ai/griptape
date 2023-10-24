from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.utils import PromptStack
import pytest


class TestHuggingFaceHubPromptDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch(
            "griptape.drivers.prompt.hugging_face_hub_prompt_driver.InferenceApi"
        ).return_value
        mock_client.task = "text-generation"
        mock_client.return_value = [{"generated_text": "model-output"}]
        return mock_client

    @pytest.fixture
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        return prompt_stack

    @pytest.fixture(autouse=True)
    def mock_autotokenizer(self, mocker):
        mock_autotokenizer = mocker.patch(
            "transformers.AutoTokenizer.from_pretrained"
        ).return_value
        mock_autotokenizer.model_max_length = 42
        return mock_autotokenizer

    def test_init(self):
        assert HuggingFaceHubPromptDriver(api_token="foobar", model="gpt2")

    def test_try_run(self, prompt_stack):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token", model="repo-id"
        )

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize("choices", [[], [1, 2]])
    def test_try_run_throws_when_multiple_choices_returned(
        self, choices, mock_client, prompt_stack
    ):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token", model="repo-id"
        )
        mock_client.return_value = choices

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        e.value.args[
            0
        ] == "completion with more than one choice is not supported yet"

    def test_try_run_throws_when_unsupported_task_returned(
        self, prompt_stack, mock_client
    ):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token", model="repo-id"
        )
        mock_client.task = "obviously-an-unsupported-task"

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0].startswith(
            "only models with the following tasks are supported: "
        )
