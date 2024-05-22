import pytest

from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.artifacts.actions_artifact import ActionsArtifact
from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.structures import Pipeline
from griptape.structures.agent import Agent
from griptape.tasks import PromptTask
from griptape.utils import PromptStack
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestBasePromptDriver:
    def test_run_via_pipeline_retries_success(self):
        driver = MockPromptDriver(max_attempts=1)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, TextArtifact)

    def test_run_via_pipeline_retries_failure(self):
        driver = MockFailingPromptDriver(max_failures=2, max_attempts=1)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, ErrorArtifact)

    def test_run_via_pipeline_publishes_events(self, mocker):
        mock_publish_event = mocker.patch.object(Pipeline, "publish_event")
        driver = MockPromptDriver()
        pipeline = Pipeline(prompt_driver=driver)
        pipeline.add_task(PromptTask("test"))

        pipeline.run()

        events = [call_args[0][0] for call_args in mock_publish_event.call_args_list]
        assert instance_count(events, StartPromptEvent) == 1
        assert instance_count(events, FinishPromptEvent) == 1

    def test_run(self):
        assert isinstance(MockPromptDriver().run(PromptStack(inputs=[])), TextArtifact)

    def test_run_with_tools(self):
        output = MockPromptDriver(use_native_tools=True).run(
            PromptStack(
                inputs=[PromptStack.Input("test", role=PromptStack.USER_ROLE)], tools=[MockTool(allowlist=["test"])]
            )
        )

        assert isinstance(output, ActionsArtifact)
        assert output.value == "mock thought"
        assert output.actions[0].tag == "test-id"
        assert output.actions[0].name == "MockTool"
        assert output.actions[0].path == "test"
        assert output.actions[0].input == {"values": {"test": "mock tool input"}}

        # Mock Prompt Driver simulates CoT by using an Action if the last input is from the user, otherwise return the answer.
        output = MockPromptDriver().run(PromptStack())
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test_run_stream(self):
        output = MockPromptDriver(stream=True, structure=Agent()).run(PromptStack(inputs=[]))

        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test_run_stream_with_tools(self):
        output = MockPromptDriver(stream=True, use_native_tools=True, structure=Agent()).run(
            PromptStack(
                inputs=[PromptStack.Input("test", role=PromptStack.USER_ROLE)], tools=[MockTool(allowlist=["test"])]
            )
        )

        assert isinstance(output, ActionsArtifact)
        assert output.value == "mock thought"
        assert output.actions[0].tag == "test-id"
        assert output.actions[0].name == "MockTool"
        assert output.actions[0].path == "test"
        assert output.actions[0].input == {"values": {"test": "mock tool input"}}

        # Mock Prompt Driver simulates CoT by using an Action if the last input is from the user, otherwise return the answer.
        output = MockPromptDriver(stream=True, structure=Agent()).run(PromptStack())
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test_run_stream_with_bad_tool_input(self):
        with pytest.raises(ValueError):
            MockPromptDriver(stream=True, use_native_tools=True, structure=Agent(), mock_tool_input='{"values":,}').run(
                PromptStack(
                    inputs=[PromptStack.Input("test", role=PromptStack.USER_ROLE)], tools=[MockTool(allowlist=["test"])]
                )
            )

    def test_token_count(self):
        assert (
            MockPromptDriver().token_count(
                PromptStack(inputs=[PromptStack.Input("foobar", role=PromptStack.USER_ROLE)])
            )
            == 24
        )

    def test_max_output_tokens(self):
        assert MockPromptDriver().max_output_tokens("foobar") == 4090
        assert MockPromptDriver(max_tokens=5000).max_output_tokens("foobar") == 4090
        assert MockPromptDriver(max_tokens=100).max_output_tokens("foobar") == 100

    def test_prompt_stack_to_string(self):
        assert (
            MockPromptDriver().prompt_stack_to_string(
                PromptStack(inputs=[PromptStack.Input("foobar", role=PromptStack.USER_ROLE)])
            )
            == "User: foobar\n\nAssistant:"
        )

    def test_custom_prompt_stack_to_string(self):
        assert (
            MockPromptDriver(
                prompt_stack_to_string=lambda stack: f"Foo: {stack.inputs[0].content}"
            ).prompt_stack_to_string(PromptStack(inputs=[PromptStack.Input("foobar", role=PromptStack.USER_ROLE)]))
            == "Foo: foobar"
        )


def instance_count(instances, clazz):
    return len([instance for instance in instances if isinstance(instance, clazz)])
