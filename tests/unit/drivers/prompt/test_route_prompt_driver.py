import pytest

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.common import PromptStack
from griptape.common.prompt_stack.contents.text_delta_message_content import TextDeltaMessageContent
from griptape.drivers import RouteLlmPromptDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestRouteLlmPromptDriver:
    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("routellm.controller.Controller")

        def side_effect(prompt, router, threshold) -> str:
            return "strong-model" if prompt == "strong-input" else "weak-model"

        mock_client.return_value.route.side_effect = side_effect

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("routellm.controller.Controller")

        def side_effect(prompt, router, threshold) -> str:
            return "strong-model" if prompt == "strong-input" else "weak-model"

        mock_client.return_value.route.side_effect = side_effect

        return mock_client

    def test_init(self):
        assert RouteLlmPromptDriver(
            threshold=0.5,
            strong_prompt_driver=MockPromptDriver(model="strong-model", mock_output="strong-output"),
            weak_prompt_driver=MockPromptDriver(model="weak-model", mock_output="weak-output"),
        )

    @pytest.mark.parametrize(
        "strong",
        [(True), (False)],
    )
    def test_try_run_strong_model(self, strong, mock_client):
        # Given
        driver = RouteLlmPromptDriver(
            threshold=0.5,
            strong_prompt_driver=MockPromptDriver(model="strong-model", mock_output="strong-output"),
            weak_prompt_driver=MockPromptDriver(model="weak-model", mock_output="weak-output"),
        )

        prompt_stack = PromptStack()
        if strong:
            prompt_stack.add_user_message("strong-input")
        else:
            prompt_stack.add_user_message("weak-input")

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.route.assert_called_once_with(
            prompt=prompt_stack.messages[-1].value,
            router=driver.router,
            threshold=driver.threshold,
        )
        if strong:
            assert message.value == "strong-output"
            assert driver.model == driver.strong_prompt_driver.model
            assert driver.tokenizer == driver.strong_prompt_driver.tokenizer
        else:
            assert message.value == "weak-output"
            assert driver.model == driver.weak_prompt_driver.model
            assert driver.tokenizer == driver.weak_prompt_driver.tokenizer

    @pytest.mark.parametrize(
        "strong",
        [(True), (False)],
    )
    def test_try_stream_run(self, strong, mock_stream_client):
        # Given
        driver = RouteLlmPromptDriver(
            threshold=0.5,
            strong_prompt_driver=MockPromptDriver(model="strong-model", mock_output="strong-output"),
            weak_prompt_driver=MockPromptDriver(model="weak-model", mock_output="weak-output"),
        )

        prompt_stack = PromptStack()
        if strong:
            prompt_stack.add_user_message("strong-input")
        else:
            prompt_stack.add_user_message("weak-input")

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_stream_client.return_value.route.assert_called_once_with(
            prompt=prompt_stack.messages[-1].value,
            router=driver.router,
            threshold=driver.threshold,
        )
        if strong:
            assert message.value == "strong-output"
            assert driver.model == driver.strong_prompt_driver.model
            assert driver.tokenizer == driver.strong_prompt_driver.tokenizer
        else:
            assert message.value == "weak-output"
            assert driver.model == driver.weak_prompt_driver.model
            assert driver.tokenizer == driver.weak_prompt_driver.tokenizer
