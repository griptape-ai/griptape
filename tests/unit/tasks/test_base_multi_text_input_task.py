from griptape.artifacts import TextArtifact
from griptape.structures import Pipeline
from tests.mocks.mock_multi_text_input_task import MockMultiTextInputTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestBaseMultiTextInputTask:
    def test_string_input(self):
        assert MockMultiTextInputTask(("foobar", "bazbar")).input[0].value == "foobar"
        assert MockMultiTextInputTask(("foobar", "bazbar")).input[1].value == "bazbar"

        task = MockMultiTextInputTask()
        task.input = ("foobar", "bazbar")
        assert task.input[0].value == "foobar"
        assert task.input[1].value == "bazbar"

    def test_artifact_input(self):
        assert MockMultiTextInputTask((TextArtifact("foobar"), TextArtifact("bazbar"))).input[0].value == "foobar"
        assert MockMultiTextInputTask((TextArtifact("foobar"), TextArtifact("bazbar"))).input[1].value == "bazbar"

        task = MockMultiTextInputTask()
        task.input = (TextArtifact("foobar"), TextArtifact("bazbar"))
        assert task.input[0].value == "foobar"
        assert task.input[1].value == "bazbar"

    def test_callable_input(self):
        assert (
            MockMultiTextInputTask((lambda _: TextArtifact("foobar"), lambda _: TextArtifact("bazbar"))).input[0].value
            == "foobar"
        )
        assert (
            MockMultiTextInputTask((lambda _: TextArtifact("foobar"), lambda _: TextArtifact("bazbar"))).input[1].value
            == "bazbar"
        )

        task = MockMultiTextInputTask()
        task.input = (lambda _: TextArtifact("foobar"), lambda _: TextArtifact("bazbar"))
        assert task.input[0].value == "foobar"
        assert task.input[1].value == "bazbar"

    def test_full_context(self):
        parent = MockMultiTextInputTask(("parent1", "parent2"))
        subtask = MockMultiTextInputTask(("test1", "test2"), context={"foo": "bar"})
        child = MockMultiTextInputTask(("child2", "child2"))
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_tasks(parent, subtask, child)

        pipeline.run()

        context = subtask.full_context

        assert context["foo"] == "bar"
        assert context["parent_output"] == parent.output.to_text()
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
