from griptape.tasks import PromptTask
from tests.mocks.mock_driver import MockDriver
from griptape.structures import Pipeline


class TestPromptStep:
    def test_run(self):
        step = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_task(step)

        assert step.run().value == "mock output"

    def test_render_prompt(self):
        step = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(step)

        assert step.render_prompt() == "test value"

    def test_full_context(self):
        parent = PromptTask("parent")
        step = PromptTask("test", context={"foo": "bar"})
        child = PromptTask("child")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_tasks(parent, step, child)

        pipeline.run()

        context = step.full_context

        assert context["foo"] == "bar"
        assert context["input"] == parent.output.value
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
