from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptSubtask:
    def test_run(self):
        subtask = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(subtask)

        assert subtask.run().to_text() == "mock output"

    def test_render_prompt(self):
        subtask = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(subtask)

        assert subtask.input.to_text() == "test value"

    def test_full_context(self):
        parent = PromptTask("parent")
        subtask = PromptTask("test", context={"foo": "bar"})
        child = PromptTask("child")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_tasks(parent, subtask, child)

        pipeline.run()

        context = subtask.full_context

        assert context["foo"] == "bar"
        assert context["parent_output"] == parent.output.to_text()
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
