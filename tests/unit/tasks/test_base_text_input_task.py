from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline
from tests.mocks.mock_text_input_task import MockTextInputTask


class TestBaseTextInputTask:
    def test_input(self):
        assert MockTextInputTask("foobar").input.value == "foobar"

    def test_full_context(self):
        parent = MockTextInputTask("parent")
        subtask = MockTextInputTask("test", context={"foo": "bar"})
        child = MockTextInputTask("child")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_tasks(parent, subtask, child)

        pipeline.run()

        context = subtask.full_context

        assert context["foo"] == "bar"
        assert context["parent_output"] == parent.output.to_text()
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
