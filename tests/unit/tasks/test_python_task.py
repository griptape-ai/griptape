from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks import PythonTask, BaseTextInputTask, BaseTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


def hello_world(task: BaseTask) -> BaseArtifact:
    greeting = "Hello World!"
    # We don't want to create an artifact, so just pass the parent task's input back
    return TextArtifact(greeting)


def deliberate_exception(task: BaseTask) -> BaseArtifact:
    raise ValueError("ugh blub")


class TestPromptSubtask:
    def test_hello_world_fn(self):
        task = PythonTask(run_fn=hello_world)

        assert task.run().value == "Hello World!"

    def test_error_fn(self):
        task = PythonTask(run_fn=deliberate_exception)

        assert task.run().value == "error during Python Task execution: ugh blub"
