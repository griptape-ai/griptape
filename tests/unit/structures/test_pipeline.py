import json
from griptape.artifacts import TextArtifact
from griptape.rules import Rule
from griptape.tokenizers import TiktokenTokenizer
from griptape.tasks import PromptTask, BaseTask
from griptape.memory import Memory
from tests.mocks.mock_driver import MockDriver
from griptape.structures import Pipeline


class TestPipeline:
    def test_constructor(self):
        rule = Rule("test")
        driver = MockDriver()
        pipeline = Pipeline(prompt_driver=driver, rules=[rule])

        assert pipeline.prompt_driver is driver
        assert pipeline.first_task() is None
        assert pipeline.last_task() is None
        assert pipeline.rules[0].value is "test"
        assert pipeline.memory is None

    def test_with_memory(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")
        third_task = PromptTask("test3")

        pipeline = Pipeline(
            prompt_driver=MockDriver(),
            memory=Memory()
        )

        pipeline.add_tasks(first_task, second_task, third_task)

        assert pipeline.memory is not None
        assert len(pipeline.memory.runs) == 0

        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(pipeline.memory.runs) == 3

    def test_tasks_order(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")
        third_task = PromptTask("test3")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_task(first_task)
        pipeline.add_task(second_task)
        pipeline.add_task(third_task)

        assert pipeline.first_task().id is first_task.id
        assert pipeline.tasks[1].id is second_task.id
        assert pipeline.tasks[2].id is third_task.id
        assert pipeline.last_task().id is third_task.id

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_task(first_task)
        pipeline.add_task(second_task)

        assert len(pipeline.tasks) == 2
        assert first_task in pipeline.tasks
        assert second_task in pipeline.tasks
        assert first_task.structure == pipeline
        assert second_task.structure == pipeline
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 1
        assert len(second_task.parents) == 1
        assert len(second_task.children) == 0

    def test_add_tasks(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_tasks(first_task, second_task)

        assert len(pipeline.tasks) == 2
        assert first_task in pipeline.tasks
        assert second_task in pipeline.tasks
        assert first_task.structure == pipeline
        assert second_task.structure == pipeline
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 1
        assert len(second_task.parents) == 1
        assert len(second_task.children) == 0

    def test_prompt_stack_without_memory(self):
        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        task1 = PromptTask("test")
        task2 = PromptTask("test")

        pipeline.add_task(task1)

        # context and first input
        assert len(pipeline.prompt_stack(task1)) == 2

        pipeline.run()

        pipeline.add_task(task2)

        # context and second input
        assert len(pipeline.prompt_stack(task2)) == 2

    def test_prompt_stack_with_memory(self):
        pipeline = Pipeline(
            prompt_driver=MockDriver(),
            memory=Memory()
        )

        task1 = PromptTask("test")
        task2 = PromptTask("test")

        pipeline.add_task(task1)

        # context and first input
        assert len(pipeline.prompt_stack(task1)) == 2

        pipeline.run()

        pipeline.add_task(task2)

        # context, memory, and second input
        assert len(pipeline.prompt_stack(task2)) == 3

    def test_to_prompt_string(self):
        pipeline = Pipeline(
            prompt_driver=MockDriver(),
        )

        task = PromptTask("test")

        pipeline.add_task(task)

        pipeline.run()

        assert "mock output" in pipeline.to_prompt_string(task)

    def test_text_artifact_token_count(self):
        text = "foobar"

        assert TextArtifact(text).token_count(TiktokenTokenizer()) == TiktokenTokenizer().token_count(text)

    def test_run(self):
        task = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockDriver())
        pipeline.add_task(task)

        assert task.state == BaseTask.State.PENDING

        result = pipeline.run()

        assert "mock output" in result.output.value
        assert task.state == BaseTask.State.FINISHED

    def test_run_with_args(self):
        task = PromptTask("{{ args[0] }}-{{ args[1] }}")
        pipeline = Pipeline(prompt_driver=MockDriver())
        pipeline.add_tasks(task)

        pipeline._execution_args = ("test1", "test2")

        assert task.input.value == "test1-test2"

        pipeline.run()

        assert task.input.value == "-"

    def test_context(self):
        parent = PromptTask("parent")
        task = PromptTask("test")
        child = PromptTask("child")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_tasks(parent, task, child)

        context = pipeline.context(task)

        assert context["input"] is None

        pipeline.run()

        context = pipeline.context(task)

        assert context["input"] == parent.output.value
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
