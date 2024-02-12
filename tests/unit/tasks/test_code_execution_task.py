from griptape.artifacts import BaseArtifact, TextArtifact, ErrorArtifact
from griptape.structures import Pipeline
from griptape.tasks import CodeExecutionTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


def hello_world(task: CodeExecutionTask) -> BaseArtifact:
    greeting = "Hello World!"
    return TextArtifact(greeting)


def non_outputting(task: CodeExecutionTask) -> BaseArtifact:
    # If your task function doesn't have an output, return task.input
    return task.input


def deliberate_exception(task: CodeExecutionTask) -> BaseArtifact:
    raise ValueError("Intentional Error")


class TestCodeExecutionTask:
    def test_hello_world_fn(self):
        task = CodeExecutionTask(run_fn=hello_world)

        assert task.run().value == "Hello World!"

    # Using a Pipeline
    # Overriding the input because we are implementing the task not the Pipeline
    def test_noop_fn(self):
        pipeline = Pipeline(prompt_driver=MockPromptDriver())
        task = CodeExecutionTask("No Op", run_fn=non_outputting)
        pipeline.add_task(task)
        temp = task.run()
        assert temp.value == "No Op"

    def test_error_fn(self):
        task = CodeExecutionTask(run_fn=deliberate_exception)

        result = task.run()

        assert isinstance(result, ErrorArtifact)
        assert result.value == "error during Code Execution Task: Intentional Error"
