from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.common import PromptStack
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


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
